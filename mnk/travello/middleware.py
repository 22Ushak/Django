from django.shortcuts import redirect
from .models import IPVisit

class RestrictIPMiddleware:
    """Middleware to track places viewed based on IP and restrict access after 2 visits."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        """Handles processing of each request."""
        response = self.get_response(request)
        return response

    def process_view(self, request, view_func, view_args, view_kwargs):
        """Restrict access after visiting 2 places based on IP and prevent reopening visited places."""
        ip = self.get_client_ip(request)

        # Allow logged-in users unrestricted access
        if request.user.is_authenticated:
            return None  

        # Track visited places only on the 'details' page
        if 'details' in request.path:
            place_id = str(view_kwargs.get('id'))  # Extract place ID

            # Retrieve visited places for this IP
            visited_places = list(IPVisit.objects.filter(ip_address=ip).values_list('place_id', flat=True))
            visited_places_count = len(visited_places)  # Count of visited places

            # If the user has already visited 2 places and is trying to visit a new one, restrict them
            if visited_places_count >= 2 and place_id not in visited_places:
                return redirect('register_first')  

            # If the user revisits a place from the same tab, restrict access
            if request.session.get('last_visited_place') == place_id:
                return redirect('register_first')  

            # Save the last visited place in the session
            request.session['last_visited_place'] = place_id

            # Log the visit if it's a new place
            if place_id not in visited_places:
                IPVisit.objects.create(ip_address=ip, place_id=place_id)

            request.session['visited_places_count'] = visited_places_count + 1  # Update count

        return None

    def get_client_ip(self, request):
        """Retrieve the real IP address of the user."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
