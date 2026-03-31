/**
 * Inventario Pro — Frontend Application
 * Conecta el dashboard HTML con la API de FastAPI.
 */

const API_URL = window.location.origin;

// ============================================
// Estado de la Aplicación
// ============================================

const state = {
    token: localStorage.getItem("token") || null,
    username: localStorage.getItem("username") || null,
    products: [],
    editingProductId: null,
};

// ============================================
// Elementos del DOM
// ============================================

const $ = (selector) => document.querySelector(selector);
const $$ = (selector) => document.querySelectorAll(selector);

const DOM = {
    // Auth
    authScreen: $("#auth-screen"),
    dashboard: $("#dashboard"),
    loginForm: $("#login-form"),
    registerForm: $("#register-form"),
    authMessage: $("#auth-message"),
    tabLogin: $("#tab-login"),
    tabRegister: $("#tab-register"),

    // Header
    userName: $("#user-name"),
    userAvatar: $("#user-avatar"),
    btnLogout: $("#btn-logout"),

    // Stats
    statProducts: $("#stat-products"),
    statStock: $("#stat-stock"),
    statLowStock: $("#stat-low-stock"),
    statValue: $("#stat-value"),

    // Products
    productsTbody: $("#products-tbody"),
    emptyState: $("#empty-state"),
    productsTable: $("#products-table"),
    searchInput: $("#search-input"),
    btnAddProduct: $("#btn-add-product"),

    // Modal
    productModal: $("#product-modal"),
    modalTitle: $("#modal-title"),
    productForm: $("#product-form"),
    btnCloseModal: $("#btn-close-modal"),
    btnCancelModal: $("#btn-cancel-modal"),
    btnSaveProduct: $("#btn-save-product"),

    // Toast
    toastContainer: $("#toast-container"),
};

// ============================================
// API Helper
// ============================================

async function api(endpoint, options = {}) {
    const headers = {
        "Content-Type": "application/json",
        ...options.headers,
    };

    if (state.token) {
        headers["Authorization"] = `Bearer ${state.token}`;
    }

    const response = await fetch(`${API_URL}${endpoint}`, {
        ...options,
        headers,
    });

    const data = await response.json();

    if (!response.ok) {
        throw new Error(data.detail || "Error en la solicitud");
    }

    return data;
}

// ============================================
// Toast Notifications
// ============================================

function showToast(message, type = "info") {
    const icons = {
        success: "✅",
        error: "❌",
        warning: "⚠️",
        info: "ℹ️",
    };

    const toast = document.createElement("div");
    toast.className = `toast toast-${type}`;
    toast.innerHTML = `
        <span class="toast-icon">${icons[type]}</span>
        <span class="toast-message">${message}</span>
    `;

    DOM.toastContainer.appendChild(toast);

    setTimeout(() => {
        toast.classList.add("toast-exit");
        setTimeout(() => toast.remove(), 300);
    }, 3500);
}

// ============================================
// Auth Functions
// ============================================

function showAuthMessage(message, type) {
    DOM.authMessage.textContent = message;
    DOM.authMessage.className = `auth-message ${type}`;
    DOM.authMessage.classList.remove("hidden");
    setTimeout(() => DOM.authMessage.classList.add("hidden"), 4000);
}

function setButtonLoading(button, loading) {
    const text = button.querySelector(".btn-text");
    const loader = button.querySelector(".btn-loader");
    if (text) text.classList.toggle("hidden", loading);
    if (loader) loader.classList.toggle("hidden", !loading);
    button.disabled = loading;
}

async function handleLogin(e) {
    e.preventDefault();
    const btn = $("#btn-login");
    setButtonLoading(btn, true);

    try {
        const formData = new URLSearchParams();
        formData.append("username", $("#login-username").value);
        formData.append("password", $("#login-password").value);

        const data = await fetch(`${API_URL}/auth/login`, {
            method: "POST",
            body: formData,
            headers: { "Content-Type": "application/x-www-form-urlencoded" },
        }).then((r) => r.json());

        if (!data.access_token) {
            throw new Error(data.detail || "Credenciales incorrectas");
        }

        state.token = data.access_token;
        state.username = $("#login-username").value;
        localStorage.setItem("token", state.token);
        localStorage.setItem("username", state.username);

        showDashboard();
        showToast(`¡Bienvenido, ${state.username}!`, "success");
    } catch (err) {
        showAuthMessage(err.message, "error");
    } finally {
        setButtonLoading(btn, false);
    }
}

async function handleRegister(e) {
    e.preventDefault();
    const btn = $("#btn-register");
    setButtonLoading(btn, true);

    try {
        await api("/auth/register", {
            method: "POST",
            body: JSON.stringify({
                username: $("#register-username").value,
                password: $("#register-password").value,
            }),
        });

        showAuthMessage("¡Cuenta creada! Ahora podés iniciar sesión.", "success");

        // Cambiar a la pestaña de login
        switchTab("login");
        $("#login-username").value = $("#register-username").value;
        $("#login-password").focus();
    } catch (err) {
        showAuthMessage(err.message, "error");
    } finally {
        setButtonLoading(btn, false);
    }
}

function handleLogout() {
    state.token = null;
    state.username = null;
    localStorage.removeItem("token");
    localStorage.removeItem("username");
    showAuthScreen();
}

// ============================================
// Navigation
// ============================================

function showAuthScreen() {
    DOM.authScreen.classList.remove("hidden");
    DOM.dashboard.classList.add("hidden");
    // Reset forms
    DOM.loginForm.reset();
    DOM.registerForm.reset();
}

function showDashboard() {
    DOM.authScreen.classList.add("hidden");
    DOM.dashboard.classList.remove("hidden");

    // Update user info
    DOM.userName.textContent = state.username;
    DOM.userAvatar.textContent = state.username.charAt(0).toUpperCase();

    // Load products
    loadProducts();
}

function switchTab(tab) {
    $$(".auth-tab").forEach((t) => t.classList.remove("active"));
    $$(".auth-form").forEach((f) => f.classList.remove("active"));

    $(`[data-tab="${tab}"]`).classList.add("active");
    $(`#${tab}-form`).classList.add("active");
}

// ============================================
// Products CRUD
// ============================================

async function loadProducts() {
    try {
        state.products = await api("/productos/");
        renderProducts(state.products);
        updateStats();
    } catch (err) {
        showToast("Error al cargar los productos", "error");
    }
}

function renderProducts(products) {
    if (products.length === 0) {
        DOM.productsTable.classList.add("hidden");
        DOM.emptyState.classList.remove("hidden");
        return;
    }

    DOM.productsTable.classList.remove("hidden");
    DOM.emptyState.classList.add("hidden");

    DOM.productsTbody.innerHTML = products
        .map((p) => {
            const status = getStockStatus(p);
            return `
            <tr data-id="${p.id}">
                <td>
                    <div class="product-name-cell">
                        <span class="product-name">${escapeHtml(p.name)}</span>
                        ${p.description ? `<span class="product-description">${escapeHtml(p.description)}</span>` : ""}
                    </div>
                </td>
                <td>$${formatNumber(p.price)}</td>
                <td><strong>${p.stock}</strong></td>
                <td>${p.min_stock}</td>
                <td><span class="badge ${status.class}">${status.icon} ${status.label}</span></td>
                <td>
                    <div class="actions-cell">
                        <button class="btn btn-success btn-sm" onclick="sellProduct(${p.id})" title="Vender 1 unidad" ${p.stock <= 0 ? "disabled" : ""}>
                            🛒 Vender
                        </button>
                        <button class="btn btn-ghost btn-sm" onclick="openEditModal(${p.id})" title="Editar">
                            ✏️
                        </button>
                        <button class="btn btn-danger btn-sm" onclick="deleteProduct(${p.id}, '${escapeHtml(p.name)}')" title="Eliminar">
                            🗑️
                        </button>
                    </div>
                </td>
            </tr>
        `;
        })
        .join("");
}

function getStockStatus(product) {
    if (product.stock <= 0) {
        return { class: "badge-critical", label: "Sin stock", icon: "🔴" };
    }
    if (product.stock <= product.min_stock) {
        return { class: "badge-low", label: "Stock bajo", icon: "🟡" };
    }
    return { class: "badge-ok", label: "Normal", icon: "🟢" };
}

function updateStats() {
    const products = state.products;
    const totalProducts = products.length;
    const totalStock = products.reduce((sum, p) => sum + p.stock, 0);
    const lowStock = products.filter((p) => p.stock <= p.min_stock && p.stock > 0).length;
    const critical = products.filter((p) => p.stock <= 0).length;
    const totalValue = products.reduce((sum, p) => sum + p.price * p.stock, 0);

    animateCounter(DOM.statProducts, totalProducts);
    animateCounter(DOM.statStock, totalStock);
    animateCounter(DOM.statLowStock, lowStock + critical);
    DOM.statValue.textContent = `$${formatNumber(totalValue)}`;
}

function animateCounter(element, target) {
    const current = parseInt(element.textContent) || 0;
    if (current === target) return;

    const duration = 400;
    const start = performance.now();

    function update(now) {
        const elapsed = now - start;
        const progress = Math.min(elapsed / duration, 1);
        const eased = 1 - Math.pow(1 - progress, 3); // easeOutCubic
        element.textContent = Math.round(current + (target - current) * eased);
        if (progress < 1) requestAnimationFrame(update);
    }

    requestAnimationFrame(update);
}

// ============================================
// Product Modal
// ============================================

function openCreateModal() {
    state.editingProductId = null;
    DOM.modalTitle.textContent = "Nuevo Producto";
    DOM.productForm.reset();
    $("#product-min-stock").value = 5;
    DOM.productModal.classList.remove("hidden");
    $("#product-name").focus();
}

function openEditModal(productId) {
    const product = state.products.find((p) => p.id === productId);
    if (!product) return;

    state.editingProductId = productId;
    DOM.modalTitle.textContent = "Editar Producto";

    $("#product-name").value = product.name;
    $("#product-description").value = product.description || "";
    $("#product-price").value = product.price;
    $("#product-stock").value = product.stock;
    $("#product-min-stock").value = product.min_stock;

    DOM.productModal.classList.remove("hidden");
    $("#product-name").focus();
}

function closeModal() {
    DOM.productModal.classList.add("hidden");
    state.editingProductId = null;
}

async function handleSaveProduct(e) {
    e.preventDefault();
    const btn = DOM.btnSaveProduct;
    setButtonLoading(btn, true);

    const productData = {
        name: $("#product-name").value.trim(),
        description: $("#product-description").value.trim() || null,
        price: parseFloat($("#product-price").value),
        stock: parseInt($("#product-stock").value),
        min_stock: parseInt($("#product-min-stock").value) || 5,
    };

    try {
        if (state.editingProductId) {
            await api(`/productos/${state.editingProductId}`, {
                method: "PUT",
                body: JSON.stringify(productData),
            });
            showToast(`"${productData.name}" actualizado correctamente`, "success");
        } else {
            await api("/productos/", {
                method: "POST",
                body: JSON.stringify(productData),
            });
            showToast(`"${productData.name}" agregado al inventario`, "success");
        }

        closeModal();
        await loadProducts();
    } catch (err) {
        showToast(err.message, "error");
    } finally {
        setButtonLoading(btn, false);
    }
}

// ============================================
// Product Actions
// ============================================

async function sellProduct(productId) {
    try {
        const product = await api(`/productos/${productId}/vender`, {
            method: "PUT",
        });
        showToast(`¡Venta registrada! "${product.name}" — Stock: ${product.stock}`, "success");

        if (product.stock <= product.min_stock) {
            showToast(`⚠️ "${product.name}" tiene stock bajo (${product.stock} uds)`, "warning");
        }

        await loadProducts();
    } catch (err) {
        showToast(err.message, "error");
    }
}

async function deleteProduct(productId, productName) {
    if (!confirm(`¿Estás seguro de eliminar "${productName}"?\nEsta acción no se puede deshacer.`)) {
        return;
    }

    try {
        await api(`/productos/${productId}`, { method: "DELETE" });
        showToast(`"${productName}" eliminado del inventario`, "success");
        await loadProducts();
    } catch (err) {
        showToast(err.message, "error");
    }
}

// ============================================
// Search / Filter
// ============================================

function handleSearch(e) {
    const query = e.target.value.toLowerCase().trim();
    if (!query) {
        renderProducts(state.products);
        return;
    }

    const filtered = state.products.filter(
        (p) =>
            p.name.toLowerCase().includes(query) ||
            (p.description && p.description.toLowerCase().includes(query))
    );

    renderProducts(filtered);
}

// ============================================
// Helpers
// ============================================

function escapeHtml(str) {
    const div = document.createElement("div");
    div.textContent = str;
    return div.innerHTML;
}

function formatNumber(num) {
    return num.toLocaleString("es-AR", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
}

// ============================================
// Event Listeners
// ============================================

function initEventListeners() {
    // Auth tabs
    DOM.tabLogin.addEventListener("click", () => switchTab("login"));
    DOM.tabRegister.addEventListener("click", () => switchTab("register"));

    // Auth forms
    DOM.loginForm.addEventListener("submit", handleLogin);
    DOM.registerForm.addEventListener("submit", handleRegister);

    // Logout
    DOM.btnLogout.addEventListener("click", handleLogout);

    // Products
    DOM.btnAddProduct.addEventListener("click", openCreateModal);
    DOM.searchInput.addEventListener("input", handleSearch);

    // Modal
    DOM.productForm.addEventListener("submit", handleSaveProduct);
    DOM.btnCloseModal.addEventListener("click", closeModal);
    DOM.btnCancelModal.addEventListener("click", closeModal);
    $(".modal-backdrop")?.addEventListener("click", closeModal);

    // Keyboard shortcuts
    document.addEventListener("keydown", (e) => {
        if (e.key === "Escape") closeModal();
    });
}

// ============================================
// App Init
// ============================================

function init() {
    initEventListeners();

    // Si hay token guardado, ir directo al dashboard
    if (state.token && state.username) {
        showDashboard();
    } else {
        showAuthScreen();
    }
}

// Esperar a que el DOM esté listo
document.addEventListener("DOMContentLoaded", init);
