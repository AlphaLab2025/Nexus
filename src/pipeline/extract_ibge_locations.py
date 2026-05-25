import csv
import gzip
import json
from pathlib import Path
from urllib.request import Request, urlopen


class IBGELocationExtractor:
    """
    Extracts Brazilian state and region metadata from the official IBGE API.
    """

    def __init__(self, output_dir: str = "../../data"):
        base_path = Path(__file__).parent
        self.output_dir = (base_path / output_dir).resolve()
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.url = "https://servicodados.ibge.gov.br/api/v1/localidades/estados?orderBy=nome"

    def fetch_states(self) -> list[dict]:
        request = Request(
            self.url,
            headers={
                "Accept": "application/json",
                "Accept-Encoding": "gzip",
                "User-Agent": "nexus-data-pipeline/1.0",
            },
        )

        with urlopen(request, timeout=30) as response:
            raw_data = response.read()
            encoding = response.headers.get("Content-Encoding", "")

        if encoding == "gzip" or raw_data[:2] == b"\x1f\x8b":
            raw_data = gzip.decompress(raw_data)

        data = json.loads(raw_data.decode("utf-8"))

        return [
            {
                "state_id": item["id"],
                "state_abbr": item["sigla"],
                "state_name": item["nome"],
                "region_id": item["regiao"]["id"],
                "region_abbr": item["regiao"]["sigla"],
                "region_name": item["regiao"]["nome"],
            }
            for item in data
        ]

    def save_data(
        self,
        rows: list[dict],
        filename: str = "ibge_states_regions.csv",
    ) -> None:
        file_path = self.output_dir / filename
        fieldnames = [
            "state_id",
            "state_abbr",
            "state_name",
            "region_id",
            "region_abbr",
            "region_name",
        ]

        with file_path.open("w", newline="", encoding="utf-8") as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)

        print(f"IBGE location data saved to: {file_path}")


if __name__ == "__main__":
    extractor = IBGELocationExtractor()
    states = extractor.fetch_states()
    extractor.save_data(states)
