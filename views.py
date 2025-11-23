"""
Definition of views.
"""

from datetime import datetime, timedelta
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpRequest, JsonResponse, FileResponse
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.db.models import Q
import json
import os

from app.models import Inventory

def home(request):
    """Renders the home page."""
    assert isinstance(request, HttpRequest)
    return render(
        request,
        'app/index.html',
        {
            'title': 'Home Page',
            'year': datetime.now().year,
        }
    )

def about(request):
    """Renders the about page."""
    assert isinstance(request, HttpRequest)
    return render(
        request,
        'app/about.html',
        {
            'title': 'About',
            'message': 'Your application description page.',
            'year': datetime.now().year,
        }
    )

# --- ASSET MANAGEMENT VIEWS ---
def asset_library(request):
    """Asset library with search and filter"""
    items = Inventory.objects.all().order_by('-date')
    
    # Search and filter functionality
    query = request.GET.get('q', '')
    asset_type = request.GET.get('type', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    tags_filter = request.GET.get('tags', '')
    
    if query:
        items = items.filter(
            Q(name__icontains=query) | 
            Q(description__icontains=query)
        )
    
    if asset_type:
        items = items.filter(asset_type=asset_type)
    
    if date_from:
        items = items.filter(date__gte=date_from)
    
    if date_to:
        items = items.filter(date__lte=date_to)
    
    if tags_filter:
        items = items.filter(tags__icontains=tags_filter)
    
    return render(request, 'app/library.html', {
        'items': items,
        'title': 'Asset Library',
        'search_query': query,
        'selected_type': asset_type,
        'date_from': date_from,
        'date_to': date_to,
        'tags_filter': tags_filter
    })

# --- ASSET OPERATIONS ---
def upload_asset(request):
    """Upload new asset with file"""
    if request.method == 'POST':
        try:
            name = request.POST.get('name')
            quantity = request.POST.get('quantity', 1)
            description = request.POST.get('description', '')
            asset_type = request.POST.get('asset_type', 'other')
            tags = request.POST.get('tags', '')
            
            # Create new inventory item
            item = Inventory(
                name=name,
                quantity=quantity,
                description=description,
                asset_type=asset_type,
                tags=tags,
                date=datetime.now().date()
            )
            
            # Handle file upload
            if 'file' in request.FILES:
                uploaded_file = request.FILES['file']
                item.file = uploaded_file
                item.file_size = uploaded_file.size
                
                # Auto-detect asset type if not specified
                if asset_type == 'other':
                    if uploaded_file.content_type.startswith('image/'):
                        item.asset_type = 'image'
                    elif uploaded_file.content_type.startswith('video/'):
                        item.asset_type = 'video'
                    elif uploaded_file.content_type.startswith('audio/'):
                        item.asset_type = 'audio'
                    elif uploaded_file.content_type in ['application/pdf', 'application/msword']:
                        item.asset_type = 'document'
            
            item.save()
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True, 
                    'message': f'Asset "{name}" uploaded successfully!',
                    'asset_id': item.id
                })
            
            messages.success(request, f'Asset "{name}" uploaded successfully!')
            return redirect('asset_library')
        
        except Exception as e:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'message': f'Error uploading asset: {str(e)}'})
            
            messages.error(request, f'Error uploading asset: {str(e)}')
            return redirect('asset_library')

def edit_asset(request, item_id):
    """Edit asset"""
    item = get_object_or_404(Inventory, id=item_id)
    
    if request.method == 'POST':
        try:
            item.name = request.POST.get('name')
            item.quantity = request.POST.get('quantity', 1)
            item.description = request.POST.get('description', '')
            item.asset_type = request.POST.get('asset_type', 'other')
            item.tags = request.POST.get('tags', '')
            
            # Handle file update
            if 'file' in request.FILES:
                new_file = request.FILES['file']
                item.file = new_file
                item.file_size = new_file.size
            
            item.save()
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': True, 'message': f'Asset "{item.name}" updated successfully!'})
            
            messages.success(request, f'Asset "{item.name}" updated successfully!')
            return redirect('asset_library')
        
        except Exception as e:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'message': f'Error updating asset: {str(e)}'})
            
            messages.error(request, f'Error updating asset: {str(e)}')
            return redirect('asset_library')
    
    # GET request - return JSON data
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'id': item.id,
            'name': item.name,
            'quantity': item.quantity,
            'description': item.description,
            'asset_type': item.asset_type,
            'tags': item.tags,
            'file_url': item.file.url if item.file else None
        })
    
    return redirect('asset_library')

def delete_asset(request, item_id):
    """Delete asset"""
    item = get_object_or_404(Inventory, id=item_id)
    item_name = item.name
    
    try:
        item.delete()
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': True, 'message': f'Asset "{item_name}" deleted successfully!'})
        
        messages.success(request, f'Asset "{item_name}" deleted successfully!')
        return redirect('asset_library')
    
    except Exception as e:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'message': f'Error deleting asset: {str(e)}'})
        
        messages.error(request, f'Error deleting asset: {str(e)}')
        return redirect('asset_library')

def download_asset(request, item_id):
    """Download asset file"""
    item = get_object_or_404(Inventory, id=item_id)
    if item.file:
        response = FileResponse(item.file.open(), as_attachment=True, filename=item.file.name)
        return response
    else:
        messages.error(request, "No file available for download")
        return redirect('asset_library')

# --- LOGIN VIEW WITH ROLE REDIRECTION ---
def login_view(request):
    form = AuthenticationForm(request, data=request.POST or None)
    error = None

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Admin login
        if username == 'admin':
            if password == 'admin':
                items = Inventory.objects.all().order_by('-date')
                return render(request, 'app/library.html', {
                    'title': 'Admin Library',
                    'message': 'Welcome Admin!',
                    'year': datetime.now().year,
                    'items': items,
                })
            else:
                error = "Wrong password for admin."

        # Editor login
        elif username == 'editor':
            if password == 'editor':
                items = Inventory.objects.all().order_by('-date')
                return render(request, 'app/library2.html', {
                    'title': 'Editor Library',
                    'message': 'Welcome Editor!',
                    'year': datetime.now().year,
                    'items': items,
                })
            else:
                error = "Wrong password for editor."

        # Viewer login
        elif username == 'viewer':
            if password == 'viewer':
                items = Inventory.objects.all().order_by('-date')
                return render(request, 'app/library3.html', {
                    'title': 'Viewer Library',
                    'message': 'Welcome Viewer!',
                    'year': datetime.now().year,
                    'items': items,
                })
            else:
                error = "Wrong password for viewer."

        # Unknown username
        else:
            error = f"User '{username}' does not exist."

    return render(request, 'app/login.html', {
        'form': form,
        'title': 'Login',
        'error': error
    })

# Keep your existing library views
def library_view(request):
    items = Inventory.objects.all().order_by('-date')
    return render(request, 'app/library.html', {
        'title': 'Library',
        'items': items
    })

def library2_view(request):
    """Editor Library Page"""
    items = Inventory.objects.all().order_by('-date')
    return render(request, 'app/library2.html', {
        'title': 'Editor Library',
        'message': 'Welcome to the Editor Library.',
        'year': datetime.now().year,
        'items': items,
    })

def library3_view(request):
    """Viewer Library Page"""
    items = Inventory.objects.all().order_by('-date')
    return render(request, 'app/library3.html', {
        'title': 'Viewer Library',
        'message': 'Welcome to the Viewer Library.',
        'year': datetime.now().year,
        'items': items,
    })