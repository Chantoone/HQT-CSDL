from fastapi import status, HTTPException, Depends, APIRouter
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from sqlalchemy import func
from sqlalchemy.orm import Session
from mart.database import get_db
import mart.mart_model as model
router = APIRouter(prefix="/visualization", tags=["visualization"])
@router.get("/total_revenue_by_month",status_code=status.HTTP_200_OK)
def get_revenue_by_month(db: Session = Depends(get_db)):
    results= db.query(model.MartRevenueByMonth.year,model.MartRevenueByMonth.month,model.MartRevenueByMonth.total_revenue).all()
    results_dict = [{"year": year, "month": month, "total_revenue": total_revenue} for year, month, total_revenue in results]
    
    return {"results": results_dict}
@router.get("/total_revenue_by_cinema",status_code=status.HTTP_200_OK)
def get_revenue_by_cinema(db: Session = Depends(get_db)):
    results= db.query(model.MartRevenueByCinema.cinema_name,model.MartRevenueByCinema.total_revenue,model.MartRevenueByCinema.year,model.MartRevenueByCinema.month).all()
    results_dict = [{"cinema_name": cinema_name, "total_revenue": total_revenue,"year":year,"month":month
                     } for cinema_name, total_revenue, year ,month in results]
    
    return {"results": results_dict}
@router.get("/top_film_revenue",status_code=status.HTTP_200_OK)
def get_revenue_by_cinema(db: Session = Depends(get_db)):
    results= db.query(model.MartTopFilmRevenue.film_title,model.MartTopFilmRevenue.total_revenue,model.MartTopFilmRevenue.year,model.MartTopFilmRevenue.month).all()
    results_dict = [{"cinema_name": film_title, "total_revenue": total_revenue,"year":year,"month":month
                     } for film_title, total_revenue, year ,month in results]
    
    return {"results": results_dict}
@router.get("/promotion_ratio", status_code=status.HTTP_200_OK)
def get_promotion_ratio(db: Session = Depends(get_db)):

    results = db.query(model.MartPromotionRatioMonthly).all()

  
    results_dict = [
        {"year": result.year, "month": result.month, "used_ratio": result.used_ratio,"not_used_ratio": result.not_used_count,"used_count": result.used_count}
        for result in results
    ]
    
    return {"results": results_dict}
@router.get("/payment_method",status_code=status.HTTP_200_OK)
def get_payment_method(db: Session = Depends(get_db)):
    results= db.query(model.MartPaymentMethodMonthly).all()
    results_dict = [{"payment_method_name":result.payment_method_name,"year":result.year,"month":result.month,"transaction_count":result.transaction_count,"total_revenue":result.total_revenue} for result in results]
    
    return {"results": results_dict}
@router.get("/top_film_rating",status_code=status.HTTP_200_OK)
def get_top_film_rating(db: Session = Depends(get_db)):
    results=db.query(model.MartFilmRatingSummary).order_by(model.MartFilmRatingSummary.avg_rating.desc()).limit(10).all()
    results_dict = [{"film_title":result.film_title,"avg_rating":result.avg_rating,"total_reviews":result.total_reviews} for result in results]
    return {"results": results_dict}