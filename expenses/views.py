from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib import messages

def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registration successful. Welcome!')
            return redirect('dashboard')
    else:
        form = UserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})

from django.contrib.auth.decorators import login_required
from .models import Expense, Category
from .forms import ExpenseForm, CategoryForm
from django.db.models import Sum
from django.shortcuts import get_object_or_404

import json
from datetime import datetime, timedelta
from django.db.models.functions import TruncMonth

@login_required
def dashboard(request):
    expenses = Expense.objects.filter(user=request.user).order_by('-date')
    total_expenses = expenses.aggregate(Sum('amount'))['amount__sum'] or 0
    categories = Category.objects.filter(user=request.user)
    
    # 1. Donut Chart (Expenses by Category)
    category_labels = []
    category_data = []
    category_sums = expenses.values('category__name').annotate(total=Sum('amount')).order_by('-total')
    for item in category_sums:
        name = item['category__name'] if item['category__name'] else 'Uncategorized'
        category_labels.append(name)
        category_data.append(float(item['total']))
        
    # 2. Area Chart (Last 7 Days)
    today = datetime.now().date()
    last_7_days = [(today - timedelta(days=i)) for i in range(6, -1, -1)]
    area_labels = [d.strftime('%b %d') for d in last_7_days]
    area_data = []
    for d in last_7_days:
        daily_sum = expenses.filter(date=d).aggregate(Sum('amount'))['amount__sum'] or 0
        area_data.append(float(daily_sum))
        
    # 3. Bar Chart (Last 6 Months)
    monthly_sums = expenses.annotate(month=TruncMonth('date')).values('month').annotate(total=Sum('amount')).order_by('month')
    bar_labels = []
    bar_data = []
    for i in range(5, -1, -1):
        # Calculate month date safely
        month_date = (today.replace(day=1) - timedelta(days=30 * i)).replace(day=1)
        bar_labels.append(month_date.strftime('%b %Y'))
        month_sum = 0
        for m_item in monthly_sums:
            if m_item['month'] and m_item['month'].year == month_date.year and m_item['month'].month == month_date.month:
                month_sum = float(m_item['total'])
                break
        bar_data.append(month_sum)
    
    context = {
        'expenses': expenses[:10], # Show last 10 expenses
        'total_expenses': total_expenses,
        'categories': categories,
        'donut_labels': json.dumps(category_labels),
        'donut_data': json.dumps(category_data),
        'area_labels': json.dumps(area_labels),
        'area_data': json.dumps(area_data),
        'bar_labels': json.dumps(bar_labels),
        'bar_data': json.dumps(bar_data),
    }
    return render(request, 'expenses/dashboard.html', context)

from django.core.paginator import Paginator

@login_required
def expense_list(request):
    expenses = Expense.objects.filter(user=request.user).order_by('-date')
    
    # Optional search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        expenses = expenses.filter(description__icontains=search_query)
        
    paginator = Paginator(expenses, 10) # Show 10 expenses per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
        
    return render(request, 'expenses/expense_list.html', {'expenses': page_obj, 'search_query': search_query})

@login_required
def add_expense(request):
    if request.method == 'POST':
        form = ExpenseForm(request.POST, request.FILES)
        if form.is_valid():
            expense = form.save(commit=False)
            expense.user = request.user
            expense.save()
            messages.success(request, 'Expense added successfully!')
            return redirect('expense_list')
    else:
        form = ExpenseForm()
    # Filter categories so the user only sees their own
    form.fields['category'].queryset = Category.objects.filter(user=request.user)
    return render(request, 'expenses/add_expense.html', {'form': form})

@login_required
def edit_expense(request, pk):
    expense = get_object_or_404(Expense, pk=pk, user=request.user)
    if request.method == 'POST':
        form = ExpenseForm(request.POST, request.FILES, instance=expense)
        if form.is_valid():
            form.save()
            messages.success(request, 'Expense updated successfully!')
            return redirect('expense_list')
    else:
        form = ExpenseForm(instance=expense)
    form.fields['category'].queryset = Category.objects.filter(user=request.user)
    return render(request, 'expenses/edit_expense.html', {'form': form, 'expense': expense})

@login_required
def delete_expense(request, pk):
    expense = get_object_or_404(Expense, pk=pk, user=request.user)
    if request.method == 'POST':
        expense.delete()
        messages.success(request, 'Expense deleted successfully!')
        return redirect('expense_list')
    return render(request, 'expenses/delete_expense.html', {'expense': expense})

@login_required
def category_list(request):
    categories = Category.objects.filter(user=request.user)
    
    # Optional search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        categories = categories.filter(name__icontains=search_query)
        
    paginator = Paginator(categories, 10) # Show 10 categories per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
        
    return render(request, 'expenses/category_list.html', {'categories': page_obj, 'search_query': search_query})

@login_required
def add_category(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            category = form.save(commit=False)
            category.user = request.user
            category.save()
            messages.success(request, 'Category added successfully!')
            return redirect('category_list')
    else:
        form = CategoryForm()
    return render(request, 'expenses/add_category.html', {'form': form})

@login_required
def edit_category(request, pk):
    category = get_object_or_404(Category, pk=pk, user=request.user)
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category updated successfully!')
            return redirect('category_list')
    else:
        form = CategoryForm(instance=category)
    return render(request, 'expenses/edit_category.html', {'form': form, 'category': category})

@login_required
def delete_category(request, pk):
    category = get_object_or_404(Category, pk=pk, user=request.user)
    if request.method == 'POST':
        category.delete()
        messages.success(request, 'Category deleted successfully!')
        return redirect('category_list')
    return render(request, 'expenses/delete_category.html', {'category': category})

from .models import UserProfile
from .forms import UserProfileForm

@login_required
def settings_view(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Settings updated successfully!')
            return redirect('settings')
    else:
        form = UserProfileForm(instance=profile)
    return render(request, 'expenses/settings.html', {'form': form})

import csv
from django.http import HttpResponse

@login_required
def export_excel(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="expenses.csv"'

    writer = csv.writer(response)
    writer.writerow(['Date', 'Description', 'Category', 'Amount'])

    expenses = Expense.objects.filter(user=request.user).order_by('-date')
    
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    if start_date:
        expenses = expenses.filter(date__gte=start_date)
    if end_date:
        expenses = expenses.filter(date__lte=end_date)
        
    for expense in expenses:
        category_name = expense.category.name if expense.category else 'Uncategorized'
        writer.writerow([expense.date.strftime('%Y-%m-%d'), expense.description, category_name, expense.amount])

    return response

from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

@login_required
def export_pdf(request):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="expenses.pdf"'

    doc = SimpleDocTemplate(response, pagesize=letter)
    elements = []
    
    styles = getSampleStyleSheet()
    elements.append(Paragraph('Expense Report', styles['Title']))
    elements.append(Spacer(1, 12))

    data = [['Date', 'Description', 'Category', 'Amount']]
    expenses = Expense.objects.filter(user=request.user).order_by('-date')
    
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    if start_date:
        expenses = expenses.filter(date__gte=start_date)
    if end_date:
        expenses = expenses.filter(date__lte=end_date)
    
    total = 0
    for expense in expenses:
        category_name = expense.category.name if expense.category else 'Uncategorized'
        data.append([
            expense.date.strftime('%Y-%m-%d'), 
            expense.description, 
            category_name, 
            f"{expense.amount:.2f}"
        ])
        total += expense.amount
        
    data.append(['', '', 'Total', f"{total:.2f}"])

    t = Table(data)
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTNAME', (2, -1), (2, -1), 'Helvetica-Bold'),
        ('FONTNAME', (3, -1), (3, -1), 'Helvetica-Bold'),
    ]))
    
    elements.append(t)
    doc.build(elements)
    
    return response

@login_required
def report_view(request):
    return render(request, 'expenses/report.html')

