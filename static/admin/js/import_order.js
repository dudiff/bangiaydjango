(function($) {
    $(document).ready(function() {
        // Hide size field initially and handle existing rows
        function initializeSizeFields() {
            $('.field-size').each(function() {
                var row = $(this).closest('tr');
                var productSelect = row.find('select[id$="-product"]');
                if (productSelect.val()) {
                    handleProductChange(row);
                } else {
                    $(this).hide();
                }
            });
        }

        // Show size field and update size options when product is selected
        function handleProductChange(row) {
            var productSelect = $(row).find('select[id$="-product"]');
            var sizeField = $(row).find('.field-size');
            var sizeSelect = $(row).find('select[id$="-size"]');
            
            if (productSelect.val()) {
                sizeField.show();
                // Clear previous size options
                sizeSelect.empty().append('<option value="">---------</option>');
                
                // Get sizes for selected product
                $.ajax({
                    url: '/admin/api/product-sizes/',
                    data: { 'product_id': productSelect.val() },
                    success: function(sizes) {
                        sizes.forEach(function(size) {
                            sizeSelect.append(
                                $('<option></option>')
                                .attr('value', size.id)
                                .text(size.name)
                            );
                        });
                    },
                    error: function() {
                        console.log('Error fetching sizes');
                    }
                });
            } else {
                sizeField.hide();
                sizeSelect.empty().append('<option value="">---------</option>');
            }
        }

        // Initialize on page load
        initializeSizeFields();

        // Handle product selection change
        $(document).on('change', 'select[id$="-product"]', function() {
            handleProductChange($(this).closest('tr'));
        });

        // Handle new rows being added
        $(document).on('formset:added', function(event, row) {
            var sizeField = $(row).find('.field-size');
            sizeField.hide();
        });
    });
})(django.jQuery);