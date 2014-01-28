class LocationMixin(object):
    """
    Used to redirect users back to filtered
    admin changelist if any filters exist

    based off [this snippet][1]

    [1]: https://djangosnippets.org/snippets/2531/
    """
    def add_view(self, request, *args, **kwargs):
        result = super(LocationMixin, self
                       ).add_view(request, *args, **kwargs)
        """
        Delete the session key, since we want the
        user to be directed to all listings
        after a save on a new object.
        """
        request.session['filtered'] = None

        return result

    def change_view(self, request, object_id, form_url='', extra_context=None):
        """
        save the referer of the page to return to the filtered
        change_list after saving the page
        """
        result = super(LocationMixin, self
                       ).change_view(request,
                                     object_id,
                                     form_url,
                                     extra_context)

        # Look at the referer for a query string '^.*\?.*$'
        ref = request.META.get('HTTP_REFERER', '')
        if ref.find('?') != -1:
            # We've got a query string, set the session value
            request.session['filtered'] = ref

        if '_save' in request.POST:
            """
            We only kick into action if we've saved and if
            there is a session key of 'filtered', then we
            delete the key.
            """
            try:
                if request.session['filtered'] is not None:
                    result['Location'] = request.session['filtered']
                    request.session['filtered'] = None
            except:
                pass

        return result
