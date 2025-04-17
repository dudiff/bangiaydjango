(function($) {
    $(document).ready(function() {
        // Function to update size options when product changes
        function updateSizeOptions() {
            $('.field-product select').each(function(index) {
                $(this).off('change').on('change', function() {
                    var productId = $(this).val();
                    var row = $(this).closest('tr');
                    var sizeSelect = row.find('.field-size select');
                    
                    if (productId) {
                        // Clear current options
                        sizeSelect.empty();
                        
                        // Fetch sizes for the selected product
                        $.ajax({
                            url: '/imports/get-product-sizes/',
                            data: {
                                'product_id': productId
                            },
                            dataType: 'json',
                            success: function(data) {
                                console.log("Received sizes for product " + productId + ":", data);
                                
                                // Add options for each size
                                $.each(data, function(i, size) {
                                    sizeSelect.append($('<option></option>')
                                        .attr('value', size.id)
                                        .text(size.name));
                                });
                                
                                // Enable the size select
                                sizeSelect.prop('disabled', false);
                            },
                            error: function(xhr, status, error) {
                                console.error("Error fetching sizes:", error);
                                sizeSelect.prop('disabled', true);
                            }
                        });
                    } else {
                        // If no product selected, disable size select
                        sizeSelect.empty();
                        sizeSelect.prop('disabled', true);
                    }
                });
            });
        }
        
        // Initial setup
        updateSizeOptions();
        
        // Update when new inline forms are added
        $(document).on('formset:added', function(event, $row, formsetName) {
            updateSizeOptions();
        });
    });
})(django.jQuery);