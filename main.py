from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from configs.database import Base, engine
from role.routers import role
from user.routers import user
from user_role.routers import user_role
from auth_credential.routers import auth_credential
from authen.routers import authen
from cinema.routers import cinema
from room.routers import room
from seat.routers import seat
from film.routers import film
from genre.routers import genre
from film_genre.routers import film_genre
from rate.routers import rate
from showtime.routers import showtime
from showtime_seat.routers import showtime_seat
from ticket.routers import ticket
from food.routers import food
from bill.routers import bill
from promotion.routers import promotion
from bill_prom.routers import bill_prom
from user_bill.routers import user_bill


import uvicorn


Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"message": "Hello World"}


app.router.include_router(role.router)
app.router.include_router(user.router)
app.router.include_router(user_role.router)
app.router.include_router(auth_credential.router)
app.router.include_router(authen.router)
app.router.include_router(cinema.router)
app.router.include_router(room.router)
app.router.include_router(seat.router)
app.router.include_router(film.router)
app.router.include_router(genre.router)
app.router.include_router(film_genre.router)
app.router.include_router(rate.router)
app.router.include_router(showtime.router)
app.router.include_router(showtime_seat.router)
app.router.include_router(ticket.router)
app.router.include_router(food.router)
app.router.include_router(bill.router)
app.router.include_router(promotion.router)
app.router.include_router(bill_prom.router)
app.router.include_router(user_bill.router)




# if __name__ == "__main__":
#     uvicorn.run(app, host=settings.host, port=settings.port)
    
