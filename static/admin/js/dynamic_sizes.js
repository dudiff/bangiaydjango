(function($) {
    $(document).ready(function() {
        function updateSizes(row) {
            var productSelect = $(row).find('select[id$="-product"]');
            var sizeSelect = $(row).find('select[id$="-size"]');
            
            if (productSelect.val()) {
                var productId = productSelect.val();
                $.ajax({
                    url: '/admin/products/product/' + productId + '/sizes/',
                    type: 'GET',
                    success: function(data) {
                        sizeSelect.empty();
                        sizeSelect.append($('<option value="">---------</option>'));
                        $.each(data, function(index, size) {
                            sizeSelect.append($('<option value="' + size.id + '">' + size.name + '</option>'));
                        });
                    }
                });
            } else {
                sizeSelect.empty();
                sizeSelect.append($('<option value="">---------</option>'));
            }
        }

        // Initial load for existing rows
        $('.dynamic-importorderitem').each(function() {
            updateSizes(this);
        });

        // On product change
        $(document).on('change', 'select[id$="-product"]', function() {
            updateSizes($(this).closest('tr'));
        });
    });
})(django.jQuery);