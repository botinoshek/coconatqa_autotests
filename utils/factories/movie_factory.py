from faker import Faker
from utils.data_generator import DataGenerator
faker = Faker()

generate_location = DataGenerator.generate_location()
generate_location_patch = DataGenerator.generate_location()

def movie_factory(
        name=None,
        imageUrl=None,
        price=None,
        description=None,
        location=None,
        published=None,
        genreId=None,
):
    return {
        "name": name or faker.word(),
        "imageUrl": imageUrl or faker.image_url(width=300, height=200),
        "price": price if price is not None else faker.random_int(1, 200),
        "description": description or faker.text(),
        "location": location or f"{generate_location}",
        "published": published if published is not None else faker.boolean(),
        "genreId": genreId if genreId is not None else faker.random_int(1, 10),
    }

