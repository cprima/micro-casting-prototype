"""Command-line interface for sitemap crawler."""

import click
from pathlib import Path
from tqdm import tqdm
from .config import Config
from .storage import LocalStorage
from .crawler import SitemapCrawler
from .logging_config import configure_logging, get_logger

logger = get_logger(__name__)


@click.group()
@click.option('--config', default='config.yaml', help='Path to config file')
@click.option('--log-level', default='INFO', type=click.Choice(['DEBUG', 'INFO', 'WARNING', 'ERROR'], case_sensitive=False), help='Logging level')
@click.option('--log-file', default=None, help='Path to log file (default: logs/sitemap-crawler.log)')
@click.pass_context
def cli(ctx, config, log_level, log_file):
    """Sitemap Crawler - Extract documentation from sitemaps and llms.txt files."""
    ctx.ensure_object(dict)

    # Initialize logging
    configure_logging(
        log_level=log_level.upper(),
        log_file=log_file,
        enable_json_file=True,
        enable_console=True
    )

    try:
        ctx.obj['config'] = Config(config)
    except FileNotFoundError:
        click.echo(f"Error: Config file not found: {config}", err=True)
        click.echo("Please create a config.yaml file or specify --config path", err=True)
        ctx.exit(1)


@cli.command()
@click.pass_context
def list(ctx):
    """List all configured sites."""
    config = ctx.obj['config']
    sites = config.get_sites()

    if not sites:
        click.echo("No sites configured.")
        return

    click.echo(f"Configured sites ({len(sites)}):\n")
    for site in sites:
        name = site.get('name', 'unnamed')
        domain = site.get('domain', 'unknown')
        source = site.get('source', 'unknown')
        site_type = site.get('type', 'unknown')

        click.echo(f"  • {name}")
        click.echo(f"    Domain:  {domain}")
        click.echo(f"    Source:  {source}")
        click.echo(f"    Type:    {site_type}")
        click.echo()


@cli.command()
@click.argument('name')
@click.option('--dry-run', is_flag=True, help='Preview URLs without crawling')
@click.pass_context
def crawl(ctx, name, dry_run):
    """Crawl a single site by name."""
    config = ctx.obj['config']

    # Get site configuration
    try:
        site_config = config.get_site_by_name(name)
    except ValueError as e:
        click.echo(f"Error: {e}", err=True)
        ctx.exit(1)

    # Setup storage (uses per-site base_dir if configured)
    base_output_dir = config.get_site_base_dir(site_config)
    storage = LocalStorage(base_output_dir)

    # Get resilience configuration
    retry_config = config.get_retry_config()
    rate_limit_config = config.get_rate_limit_config()
    http_config = config.get_http_config()
    limits_config = config.get_limits_config()
    robots_config = config.get_robots_config()

    # Get browser configuration (crawl4ai BrowserConfig)
    browser_config = config.get_browser_config()

    # Create crawler and run
    crawler = SitemapCrawler(
        site_config,
        storage,
        dry_run=dry_run,
        retry_config=retry_config,
        rate_limit_config=rate_limit_config,
        http_config=http_config,
        limits_config=limits_config,
        robots_config=robots_config,
        browser_config=browser_config
    )

    try:
        stats = crawler.crawl()

        # Print summary
        click.echo("\nCrawl Summary:")
        click.echo(f"  URLs total:    {stats.get('urls_total', 0)}")
        if not dry_run:
            click.echo(f"  URLs success:  {stats.get('urls_success', 0)}")
            click.echo(f"  URLs failed:   {stats.get('urls_failed', 0)}")
            click.echo(f"  MB downloaded: {stats.get('mb_downloaded', 0):.2f}")
            click.echo(f"  Duration (s):  {stats.get('duration_seconds', 0):.2f}")
            click.echo(f"  Speed (URL/s): {stats.get('urls_per_second', 0):.2f}")

    except Exception as e:
        logger.error("crawl_command_failed", site=name, error=str(e), exc_info=True)
        click.echo(f"Error during crawl: {e}", err=True)
        ctx.exit(1)


@cli.command()
@click.option('--dry-run', is_flag=True, help='Preview URLs without crawling')
@click.pass_context
def crawl_all(ctx, dry_run):
    """Crawl all configured sites."""
    config = ctx.obj['config']
    sites = config.get_sites()

    if not sites:
        click.echo("No sites configured.")
        return

    total_stats = {
        "urls_total": 0,
        "urls_success": 0,
        "urls_failed": 0,
        "bytes_downloaded": 0,
        "mb_downloaded": 0.0,
        "duration_seconds": 0.0
    }

    # Progress bar for sites
    sites_progress = tqdm(
        sites,
        desc="Sites",
        unit="site",
        position=0,
        leave=True
    )

    for site_config in sites_progress:
        site_name = site_config.get('name', 'unnamed')
        sites_progress.set_postfix_str(site_name, refresh=False)

        click.echo(f"\n{'='*60}")
        click.echo(f"Crawling: {site_name}")
        click.echo(f"{'='*60}\n")

        # Setup storage for this site (each site may have different base_dir)
        base_output_dir = config.get_site_base_dir(site_config)
        storage = LocalStorage(base_output_dir)

        # Get resilience configuration
        retry_config = config.get_retry_config()
        rate_limit_config = config.get_rate_limit_config()
        http_config = config.get_http_config()
        limits_config = config.get_limits_config()
        robots_config = config.get_robots_config()

        # Get browser configuration (crawl4ai BrowserConfig)
        browser_config = config.get_browser_config()

        crawler = SitemapCrawler(
            site_config,
            storage,
            dry_run=dry_run,
            retry_config=retry_config,
            rate_limit_config=rate_limit_config,
            http_config=http_config,
            limits_config=limits_config,
            robots_config=robots_config,
            browser_config=browser_config
        )

        try:
            stats = crawler.crawl()
            total_stats["urls_total"] += stats.get("urls_total", 0)
            total_stats["urls_success"] += stats.get("urls_success", 0)
            total_stats["urls_failed"] += stats.get("urls_failed", 0)
            total_stats["bytes_downloaded"] += stats.get("bytes_downloaded", 0)
            total_stats["mb_downloaded"] += stats.get("mb_downloaded", 0)
            total_stats["duration_seconds"] += stats.get("duration_seconds", 0)
        except Exception as e:
            logger.error("crawl_all_site_failed", site=site_name, error=str(e), exc_info=True)
            click.echo(f"Error crawling {site_name}: {e}", err=True)

    # Print overall summary
    click.echo(f"\n{'='*60}")
    click.echo("Overall Summary:")
    click.echo(f"{'='*60}")
    click.echo(f"  Sites:         {len(sites)}")
    click.echo(f"  URLs total:    {total_stats['urls_total']}")
    if not dry_run:
        click.echo(f"  URLs success:  {total_stats['urls_success']}")
        click.echo(f"  URLs failed:   {total_stats['urls_failed']}")
        click.echo(f"  MB downloaded: {total_stats['mb_downloaded']:.2f}")
        click.echo(f"  Duration (s):  {total_stats['duration_seconds']:.2f}")


if __name__ == '__main__':
    cli()
