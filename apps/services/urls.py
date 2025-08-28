# apps/services/urls.py
from django.urls import path
from .views import ServiceDetailView, ServicesDirectoryView

app_name = 'services'

urlpatterns = [
    path('', ServicesDirectoryView.as_view(), name='services_directory'),
    # Book Printing Services
    path('childrens-book-printing/', ServiceDetailView.as_view(), {'service_slug': 'childrens-book-printing'}, name='childrens_book_printing'),
    path('comic-book-printing/', ServiceDetailView.as_view(), {'service_slug': 'comic-book-printing'}, name='comic_book_printing'),
    path('coffee-table-book-printing/', ServiceDetailView.as_view(), {'service_slug': 'coffee-table-book-printing'}, name='coffee_table_book_printing'),
    path('coloring-book-printing/', ServiceDetailView.as_view(), {'service_slug': 'coloring-book-printing'}, name='coloring_book_printing'),
    path('art-book-printing/', ServiceDetailView.as_view(), {'service_slug': 'art-book-printing'}, name='art_book_printing'),
    path('annual-reports-printing/', ServiceDetailView.as_view(), {'service_slug': 'annual-reports-printing'}, name='annual_reports_printing'),
    path('year-book-printing/', ServiceDetailView.as_view(), {'service_slug': 'year-book-printing'}, name='year_book_printing'),
    path('on-demand-books-printing/', ServiceDetailView.as_view(), {'service_slug': 'on-demand-books-printing'}, name='on_demand_books_printing'),
    
    # Paper Box Services
    path('medical-paper-boxes/', ServiceDetailView.as_view(), {'service_slug': 'medical-paper-boxes'}, name='medical_paper_boxes'),
    path('cosmetic-paper-boxes/', ServiceDetailView.as_view(), {'service_slug': 'cosmetic-paper-boxes'}, name='cosmetic_paper_boxes'),
    path('retail-paper-boxes/', ServiceDetailView.as_view(), {'service_slug': 'retail-paper-boxes'}, name='retail_paper_boxes'),
    path('folding-carton-boxes/', ServiceDetailView.as_view(), {'service_slug': 'folding-carton-boxes'}, name='folding_carton_boxes'),
    path('corrugated-boxes/', ServiceDetailView.as_view(), {'service_slug': 'corrugated-boxes'}, name='corrugated_boxes'),
    path('kraft-boxes/', ServiceDetailView.as_view(), {'service_slug': 'kraft-boxes'}, name='kraft_boxes'),
    
    # Marketing Products
    path('brochures/', ServiceDetailView.as_view(), {'service_slug': 'brochures'}, name='brochures'),
    path('catalogue/', ServiceDetailView.as_view(), {'service_slug': 'catalogue'}, name='catalogue'),
    path('poster/', ServiceDetailView.as_view(), {'service_slug': 'poster'}, name='poster'),
    path('flyers/', ServiceDetailView.as_view(), {'service_slug': 'flyers'}, name='flyers'),
    path('dangler/', ServiceDetailView.as_view(), {'service_slug': 'dangler'}, name='dangler'),
    path('standees/', ServiceDetailView.as_view(), {'service_slug': 'standees'}, name='standees'),
    path('pen-drives/', ServiceDetailView.as_view(), {'service_slug': 'pen-drives'}, name='pen_drives'),
    
    # Stationery Products
    path('business-cards/', ServiceDetailView.as_view(), {'service_slug': 'business-cards'}, name='business_cards'),
    path('letter-head/', ServiceDetailView.as_view(), {'service_slug': 'letter-head'}, name='letter_head'),
    path('envelopes/', ServiceDetailView.as_view(), {'service_slug': 'envelopes'}, name='envelopes'),
    path('bill-book/', ServiceDetailView.as_view(), {'service_slug': 'bill-book'}, name='bill_book'),
    path('id-cards/', ServiceDetailView.as_view(), {'service_slug': 'id-cards'}, name='id_cards'),
    path('sticker/', ServiceDetailView.as_view(), {'service_slug': 'sticker'}, name='sticker'),
    path('document-printing/', ServiceDetailView.as_view(), {'service_slug': 'document-printing'}, name='document_printing'),
]