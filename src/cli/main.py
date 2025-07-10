import asyncio
from uuid import UUID

import typer
from rich import print
from rich.console import Console
from rich.table import Table
from sdk import OffersClient
from cli.cli_auth import CachedAuthClient


app = typer.Typer()
console = Console()


@app.command()
def register_product(
    id: UUID,
    name: str,
    description: str,
):
    """Register a new product."""
    async def _main():
        offers_client = OffersClient(auth_client_factory=CachedAuthClient)

        if not id:
            console.print("[red]Product ID is required.[/red]")
            return
        if not isinstance(id, UUID):
            console.print("[red]Invalid Product ID format. Must be a valid UUID.[/red]")
            return
        if not name:
            console.print("[red]Product name is required.[/red]")
            return
        if not description:
            console.print("[red]Product description is required.[/red]")
            return
        
        async with offers_client as client:
            console.print("[bold blue]Registering product...[/bold blue]")
            product = await client.products.register_product({
                "id": str(id),
                "name": name,
                "description": description,
            })
            print("[bold green]Product registered successfully![/bold green]")
            print(product)

    asyncio.run(_main())


@app.command()
def get_offers(product_id: UUID):
    """Get offers for a registered product."""
    async def _main():
        offers_client = OffersClient(auth_client_factory=CachedAuthClient)

        if not product_id:
            console.print("[red]Product ID is required.[/red]")
            return
        if not isinstance(product_id, UUID):
            console.print("[red]Invalid Product ID format. Must be a valid UUID.[/red]")
            return
        
        async with offers_client as client:
            offers = await client.offers.get_offers(product_id)

            if not offers:
                console.print("[yellow]No offers found.[/yellow]")
                return

            table = Table(title="Available Offers")
            table.add_column("ID", style="bold")
            table.add_column("Price")
            table.add_column("Stock")

            for offer in offers:
                table.add_row(str(offer.id), str(offer.price), str(offer.items_in_stock))

            console.print(table)

    asyncio.run(_main())


if __name__ == "__main__":
    app()
