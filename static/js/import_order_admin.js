(function($) {
    $(document).ready(function() {
        // Function to update size options when product changes
        function updateSizeOptions() {
            $('.field-product select').each(function(index) {
                $(this).off('change').on('change', function() {
                    var productId = $(this).val();
                    var row = $(this).closest('tr');
                    var sizeSelect = row.find('.field-size select');
                    
                    console.log("Product changed to:", productId);
                    console.log("Size select element:", sizeSelect.length ? "Found" : "Not found");
                    
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
                                console.log("Received sizes:", data);
                                
                                // Add a default option
                                sizeSelect.append($('<option></option>')
                                    .attr('value', '')
                                    .text('---------'));
                                
                                // Add options for each size
                                $.each(data, function(i, size) {
                                    sizeSelect.append($('<option></option>')
                                        .attr('value', size.id)
                                        .text(size.name));
                                });
                                
                                // Enable the size select
                                sizeSelect.prop('disabled', false);
                                
                                // Select the first size option if available
                                if (data.length > 0) {
                                    sizeSelect.val(data[0].id);
                                }
                            },
                            error: function(xhr, status, error) {
                                console.error("Error fetching sizes:", error);
                                sizeSelect.prop('disabled', true);
                            }
                        });
                    } else {
                        // If no product selected, disable size select
                        sizeSelect.empty();
                        sizeSelect.append($('<option></option>')
                            .attr('value', '')
                            .text('---------'));
                        sizeSelect.prop('disabled', true);
                    }
                });
            });
        }
        
        // Initial setup
        updateSizeOptions();
        
        // Update when new inline forms are added
        $(document).on('formset:added', function(event, $row, formsetName) {
            console.log("New form added:", formsetName);
            updateSizeOptions();
        });
        
        // Ensure size is selected before form submission
        $('form').on('submit', function(e) {
            var valid = true;
            $('.field-product select').each(function() {
                var productId = $(this).val();
                if (productId) {
                    var row = $(this).closest('tr');
                    var sizeSelect = row.find('.field-size select');
                    if (!sizeSelect.val()) {
                        alert('Please select a size for each product');
                        valid = false;
                        return false;
                    }
                }
            });
            return valid;
        });
    });
})(django.jQuery);