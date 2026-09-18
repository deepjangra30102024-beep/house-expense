from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('expense/', views.expense_list, name='expense_list'),
    path('add/', views.add_expense, name='add_expense'),
    path('edit/<int:pk>/', views.edit_expense, name='edit_expense'),
    path('delete/<int:pk>/', views.delete_expense, name='delete_expense'),
    path('category/', views.category_list, name='category_list'),
    path('category/add/', views.add_category, name='add_category'),
    path('category/edit/<int:pk>/', views.edit_category, name='edit_category'),
    path('category/delete/<int:pk>/', views.delete_category, name='delete_category'),
    path('settings/', views.settings_view, name='settings'),
    path('settings/password/', views.change_password, name='change_password'),
    path('export/excel/', views.export_excel, name='export_excel'),
    path('export/pdf/', views.export_pdf, name='export_pdf'),
    path('report/', views.report_view, name='report'),
    path('documents/', views.document_list, name='document_list'),
    path('documents/add/', views.add_document, name='add_document'),
    path('documents/edit/<int:pk>/', views.edit_document, name='edit_document'),
    path('documents/file/delete/<int:file_pk>/', views.delete_document_file, name='delete_document_file'),
    path('documents/delete/<int:pk>/', views.delete_document, name='delete_document'),
]
