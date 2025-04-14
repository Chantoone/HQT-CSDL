from typing import List
from fastapi import status, APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy import func
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from configs.database import get_db
from configs.authentication import get_current_user
from showtime_seat.models.showtime_seat import ShowtimeSeat
from ticket.models.ticket import Ticket
from ticket.schemas.ticket import *
import math


router = APIRouter(
    prefix="/tickets",
    tags=["Tickets"]
)


@router.get("/all", 
            response_model=ListTicketResponse, 
            status_code=status.HTTP_200_OK)
async def get_all_tickets(
        db: Session = Depends(get_db),
    ):
    try:
        tickets = db.query(Ticket).all()

        return ListTicketResponse(
            tickets=tickets, 
            total_data=len(tickets)
        )
    
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )
    

# @router.get("/rooms/by-film/{film_id}",
#             response_model=ListTicketResponse,
#             status_code=status.HTTP_200_OK)
# async def get_tickets_by_film(
#         film_id: int,
#         db: Session = Depends(get_db)
#     ):

#     try:
#         film = db.query(Film).filter(Film.id == film_id).first()
#         if not film:
#             raise HTTPException(
#                 status_code=status.HTTP_404_NOT_FOUND,
#                 detail="Film not found"
#             )

#         tickets = db.query(Ticket).filter(Ticket.film_id == film_id).all()

#         if not tickets:
#             raise HTTPException(
#                 status_code=status.HTTP_404_NOT_FOUND,
#                 detail="Tickets not found"
#             )

#         return ListTicketResponse(
#             tickets=tickets,
#             total_data=len(tickets)
#         )
    
#     except SQLAlchemyError as e:
#         raise HTTPException(
#             status_code=status.HTTP_409_CONFLICT,
#             detail=str(e)
#         )
    

# @router.get("/days/by-room-and-film/{room_id}/{film_id}",
#             response_model=ListTicketResponse,
#             status_code=status.HTTP_200_OK)
# async def get_tickets_by_room_and_film(
#         room_id: int,
#         film_id: int,
#         db: Session = Depends(get_db)
#     ):

#     try:
#         room = db.query(Room).filter(Room.id == room_id).first()
#         if not room:
#             raise HTTPException(
#                 status_code=status.HTTP_404_NOT_FOUND,
#                 detail="Room not found"
#             )

#         film = db.query(Film).filter(Film.id == film_id).first()
#         if not film:
#             raise HTTPException(
#                 status_code=status.HTTP_404_NOT_FOUND,
#                 detail="Film not found"
#             )

#         tickets = db.query(Ticket).filter(Ticket.room_id == room_id, Ticket.film_id == film_id).all()

#         if not tickets:
#             raise HTTPException(
#                 status_code=status.HTTP_404_NOT_FOUND,
#                 detail="Tickets not found"
#             )

#         return ListTicketResponse(
#             tickets=tickets,
#             total_data=len(tickets)
#         )
    
#     except SQLAlchemyError as e:
#         raise HTTPException(
#             status_code=status.HTTP_409_CONFLICT,
#             detail=str(e)
#         )
    

@router.get("/pageable",
            response_model=TicketPageableResponse,
            status_code=status.HTTP_200_OK)
async def get_all_tickets_pageable(
        page: int = 1,
        size: int = 10,
        db: Session = Depends(get_db)
    ):
    try:
        total_data = db.query(func.count(Ticket.id)).scalar()
        total_page = math.ceil(total_data / size)
        offset = (page - 1) * size

        tickets = db.query(Ticket).offset(offset).limit(size).all()

        return TicketPageableResponse(
            tickets=tickets,
            total_data=total_data,
            total_page=total_page
        )
    
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )
    

@router.post("/create",
             status_code=status.HTTP_201_CREATED)
async def create_ticket(
        ticket: TicketCreate,
        db: Session = Depends(get_db)
    ):
    try:
        showtime_seat = db.query(ShowtimeSeat).filter(ShowtimeSeat.id == ticket.showtime_seat_id).first()
        if not showtime_seat:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Showtime seat not found"
            )

        new_ticket = Ticket(
            title=ticket.title,
            description=ticket.description,
            price=ticket.price,
            showtime_seat_id=ticket.showtime_seat_id,
            bill_id=ticket.bill_id   
        )

        db.add(new_ticket)
        db.commit()

        return {"ticket_id": new_ticket.id}
    
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )
    
@router.get("/{ticket_id}",
            response_model=TicketResponse,
            status_code=status.HTTP_200_OK)
async def get_ticket_by_id(
        ticket_id: int,
        db: Session = Depends(get_db)
    ):
    try:
        ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()

        if not ticket:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Ticket not found"
            )

        return ticket
    
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )
    

@router.post("/search",
            response_model=ListTicketResponse,
            status_code=status.HTTP_200_OK)
async def search_tickets(
        ticket: TicketSearch,
        db: Session = Depends(get_db)
    ):
    try:
        tickets = db.query(Ticket)

        if ticket.title:
            tickets = tickets.filter(Ticket.title.ilike(f"%{ticket.title}%"))
        if ticket.description:
            tickets = tickets.filter(Ticket.description.ilike(f"%{ticket.description}%"))
        if ticket.price:
            tickets = tickets.filter(Ticket.price == ticket.price)
        if ticket.showtime_seat_id:
            tickets = tickets.filter(Ticket.showtime_seat_id == ticket.showtime_seat_id)
        
        tickets = tickets.all()

        return ListTicketResponse(
            tickets=tickets,
            total_data=len(tickets)
        )
    
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )
    


@router.put("/update/{ticket_id}")
async def update_ticket(
        ticket_id: int,
        ticket: TicketUpdate,
        db: Session = Depends(get_db)
    ):
    try:
        ticket_data = db.query(Ticket).filter(Ticket.id == ticket_id).first()

        if not ticket_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Ticket not found"
            )

        ticket_data.title = ticket.title
        ticket_data.description = ticket.description
        ticket_data.price = ticket.price
        ticket_data.showtime_seat_id = ticket.showtime_seat_id

        db.commit()

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"message": "Ticket updated successfully"}
        )
    
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )
    

@router.delete("/delete/{ticket_id}")
async def delete_ticket(
        ticket_id: int,
        db: Session = Depends(get_db)
    ):
    try:
        ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()

        if not ticket:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Ticket not found"
            )

        db.delete(ticket)
        db.commit()

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"message": "Ticket deleted successfully"}
        )
    
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )
    

@router.delete("/delete-many")
async def delete_many_tickets(
        ticket_ids: List[int],
        db: Session = Depends(get_db)
    ):
    try:
        tickets = db.query(Ticket).filter(Ticket.id.in_(ticket_ids)).all()

        if not tickets:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tickets not found"
            )

        db.delete(tickets)
        db.commit()

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"message": "Tickets deleted successfully"}
        )
    
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )