from fastapi import FastAPI
from main2 import recommend
from placeorder import place_order

app = FastAPI()

# Define routes directly if not using APIRouter
app.get("/recommend")(recommend)
app.post("/place-order")(place_order)
