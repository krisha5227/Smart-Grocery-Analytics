let posCart = [];

document.addEventListener('DOMContentLoaded', function () {
    const productSelect = document.getElementById('productSelect');
    if (productSelect) {
        productSelect.addEventListener('change', handleProductSelect);
    }

    const addToCartBtn = document.getElementById('addToCartBtn');
    if (addToCartBtn) {
        addToCartBtn.addEventListener('click', addSelectedItemToCart);
    }

    const checkoutForm = document.getElementById('posCheckoutForm');
    if (checkoutForm) {
        checkoutForm.addEventListener('submit', handleCheckoutSubmit);
    }
});

function handleProductSelect() {
    const select = document.getElementById('productSelect');
    const selectedOption = select.options[select.selectedIndex];
    const badgeEl = document.getElementById('posStockBadge');

    if (!selectedOption || !selectedOption.value) {
        document.getElementById('posPriceDisplay').value = '₹0.00';
        badgeEl.innerHTML = '<span class="text-muted">Stock: Select product</span>';
        return;
    }

    const price = selectedOption.getAttribute('data-price');
    const stock = parseInt(selectedOption.getAttribute('data-stock'));
    const reorder = parseInt(selectedOption.getAttribute('data-reorder') || '10');
    const unit = selectedOption.getAttribute('data-unit');

    document.getElementById('posPriceDisplay').value = `₹${parseFloat(price).toFixed(2)}`;

    if (stock === 0) {
        badgeEl.innerHTML = `<span class="badge-out-of-stock"><i class="bi bi-x-circle"></i> Out of Stock</span>`;
    } else if (stock <= reorder) {
        badgeEl.innerHTML = `<span class="badge-low-stock"><i class="bi bi-exclamation-triangle"></i> Low: ${stock} ${unit}</span>`;
    } else {
        badgeEl.innerHTML = `<span class="badge-in-stock"><i class="bi bi-check-circle"></i> In Stock: ${stock} ${unit}</span>`;
    }
}

function filterPosProducts() {
    const catId = document.getElementById('posCategoryFilter')?.value || '';
    const searchText = (document.getElementById('posSearchInput')?.value || '').toLowerCase().trim();
    const select = document.getElementById('productSelect');
    if (!select) return;

    const options = select.options;
    let matchCount = 0;

    for (let i = 0; i < options.length; i++) {
        const opt = options[i];
        if (!opt.value) continue;

        const optCat = opt.getAttribute('data-category');
        const optName = (opt.getAttribute('data-name') || '').toLowerCase();

        const matchesCat = !catId || optCat === catId;
        const matchesSearch = !searchText || optName.includes(searchText);

        if (matchesCat && matchesSearch) {
            opt.style.display = '';
            matchCount++;
        } else {
            opt.style.display = 'none';
        }
    }

    // Reset selection if current selection is now hidden
    const currentSelected = select.options[select.selectedIndex];
    if (currentSelected && currentSelected.value && currentSelected.style.display === 'none') {
        select.value = '';
        handleProductSelect();
    }
}

function stepQty(delta) {
    const qtyInput = document.getElementById('posQtyInput');
    if (!qtyInput) return;
    let val = parseInt(qtyInput.value) || 1;
    val = Math.max(1, val + delta);
    qtyInput.value = val;
}

function addSelectedItemToCart() {
    const select = document.getElementById('productSelect');
    const selectedOption = select.options[select.selectedIndex];
    const qtyInput = document.getElementById('posQtyInput');

    if (!selectedOption || !selectedOption.value) {
        showToast('Please select a product first.', 'warning');
        return;
    }

    const productId = parseInt(selectedOption.value);
    const productName = selectedOption.getAttribute('data-name');
    const price = parseFloat(selectedOption.getAttribute('data-price'));
    const cost = parseFloat(selectedOption.getAttribute('data-cost'));
    const stock = parseInt(selectedOption.getAttribute('data-stock'));
    const unit = selectedOption.getAttribute('data-unit');
    const quantity = parseInt(qtyInput.value);

    if (isNaN(quantity) || quantity <= 0) {
        showToast('Please enter a valid purchase quantity greater than 0.', 'warning');
        return;
    }

    // Check existing quantity in cart
    const existingIndex = posCart.findIndex(item => item.product_id === productId);
    let currentInCart = existingIndex > -1 ? posCart[existingIndex].quantity : 0;
    let newTotalQty = currentInCart + quantity;

    // Stock Validation
    if (newTotalQty > stock) {
        showToast(`Insufficient stock! Available: ${stock} ${unit}, requested total: ${newTotalQty}`, 'danger');
        return;
    }

    if (existingIndex > -1) {
        posCart[existingIndex].quantity = newTotalQty;
        posCart[existingIndex].subtotal = newTotalQty * price;
        posCart[existingIndex].profit = newTotalQty * (price - cost);
    } else {
        posCart.push({
            product_id: productId,
            product_name: productName,
            unit: unit,
            selling_price: price,
            cost_price: cost,
            stock_available: stock,
            quantity: quantity,
            subtotal: quantity * price,
            profit: quantity * (price - cost)
        });
    }

    showToast(`Added ${quantity} ${unit} of ${productName} to cart!`, 'success');

    // Reset inputs
    qtyInput.value = 1;
    renderCart();
}

function removeFromCart(index) {
    const item = posCart[index];
    posCart.splice(index, 1);
    renderCart();
    if (item) {
        showToast(`Removed ${item.product_name} from cart.`, 'info');
    }
}

function clearCart() {
    if (posCart.length === 0) return;
    if (confirm('Are you sure you want to clear all items from the cart?')) {
        posCart = [];
        renderCart();
        showToast('Cart cleared.', 'info');
    }
}

function updateCartQuantity(index, newQty) {
    const qty = parseInt(newQty);
    if (isNaN(qty) || qty <= 0) {
        removeFromCart(index);
        return;
    }

    const item = posCart[index];
    if (qty > item.stock_available) {
        showToast(`Cannot exceed available stock (${item.stock_available} ${item.unit}).`, 'danger');
        renderCart();
        return;
    }

    item.quantity = qty;
    item.subtotal = qty * item.selling_price;
    item.profit = qty * (item.selling_price - item.cost_price);
    renderCart();
}

function renderCart() {
    const tbody = document.getElementById('cartTableBody');
    if (!tbody) return;

    tbody.innerHTML = '';

    if (posCart.length === 0) {
        tbody.innerHTML = '<tr><td colspan="6" class="text-center text-muted py-4">Cart is empty. Select a product on the left to add.</td></tr>';
        document.getElementById('grandTotalDisplay').innerText = '₹0.00';
        document.getElementById('totalProfitDisplay').innerText = '₹0.00';
        document.getElementById('totalItemsDisplay').innerText = '0';
        return;
    }

    let grandTotal = 0;
    let totalProfit = 0;
    let totalItems = 0;

    posCart.forEach((item, index) => {
        grandTotal += item.subtotal;
        totalProfit += item.profit;
        totalItems += item.quantity;

        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td>
                <strong>${item.product_name}</strong>
                <div class="small text-muted">₹${item.selling_price.toFixed(2)} / ${item.unit}</div>
            </td>
            <td>
                <input type="number" class="form-control form-control-sm text-center fw-bold" style="width: 75px;" 
                       value="${item.quantity}" min="1" max="${item.stock_available}"
                       onchange="updateCartQuantity(${index}, this.value)">
            </td>
            <td>₹${item.selling_price.toFixed(2)}</td>
            <td><strong>₹${item.subtotal.toFixed(2)}</strong></td>
            <td class="text-success small fw-bold">+₹${item.profit.toFixed(2)}</td>
            <td class="text-end">
                <button type="button" class="btn btn-sm btn-outline-danger" onclick="removeFromCart(${index})" title="Remove">
                    <i class="bi bi-trash"></i>
                </button>
            </td>
        `;
        tbody.appendChild(tr);
    });

    document.getElementById('grandTotalDisplay').innerText = `₹${grandTotal.toFixed(2)}`;
    document.getElementById('totalProfitDisplay').innerText = `₹${totalProfit.toFixed(2)}`;
    document.getElementById('totalItemsDisplay').innerText = totalItems;
}

function handleCheckoutSubmit(e) {
    e.preventDefault();

    if (posCart.length === 0) {
        showToast('Cart is empty. Please add products before completing sale.', 'warning');
        return;
    }

    const customerName = document.getElementById('customerNameInput').value;
    const checkoutBtn = document.getElementById('submitSaleBtn');

    checkoutBtn.disabled = true;
    checkoutBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span> Processing Sale...';

    fetch('/sales/create', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            customer_name: customerName,
            items: posCart
        })
    })
    .then(res => res.json())
    .then(data => {
        if (data.success) {
            showToast('Sale completed successfully! Opening invoice...', 'success');
            setTimeout(() => {
                window.location.href = `/sales/invoice/${data.invoice_id}`;
            }, 600);
        } else {
            showToast(`Checkout Error: ${data.message}`, 'danger');
            checkoutBtn.disabled = false;
            checkoutBtn.innerHTML = '<i class="bi bi-check-circle me-1"></i> Complete & Generate Invoice';
        }
    })
    .catch(err => {
        console.error('Checkout error:', err);
        showToast('A network or server error occurred during checkout.', 'danger');
        checkoutBtn.disabled = false;
        checkoutBtn.innerHTML = '<i class="bi bi-check-circle me-1"></i> Complete & Generate Invoice';
    });
}
