document.addEventListener('DOMContentLoaded', () => {
  const loggedInUserKey = 'sportpathCurrentUser';
  const apiBase = window.SPORTPATH_API_URL || 'http://127.0.0.1:5000/api';
  const currentPage = window.location.pathname.split('/').pop() || 'index.html';
  const isAuthPage = currentPage === 'login.html';
  const currentUser = JSON.parse(localStorage.getItem(loggedInUserKey) || 'null');
  const isValidPhone = (phone) => /^\d{10}$/.test(phone);

  if (!currentUser && !isAuthPage) {
    window.location.replace(`login.html?returnTo=${encodeURIComponent(currentPage)}`);
    return;
  }

  if (currentUser && isAuthPage) {
    window.location.replace('index.html');
    return;
  }

  const toggle = document.querySelector('.menu-toggle');
  const nav = document.querySelector('.site-nav');

  const navWrap = document.querySelector('.nav-wrap');
  if (navWrap && currentPage !== 'index.html') {
    const backButton = document.createElement('button');
    backButton.className = 'back-button';
    backButton.type = 'button';
    backButton.setAttribute('aria-label', 'Go back to the previous page');
    backButton.innerHTML = '<span aria-hidden="true">&#8592;</span> Back';
    backButton.addEventListener('click', () => {
      if (window.history.length > 1) {
        window.history.back();
      } else {
        window.location.href = 'index.html';
      }
    });
    navWrap.insertBefore(backButton, nav);
  }

  if (toggle && nav) {
    toggle.addEventListener('click', () => {
      nav.classList.toggle('open');
    });
  }

  document.querySelectorAll('.password-toggle').forEach((button) => {
    const passwordInput = document.getElementById(button.dataset.target);
    if (!passwordInput) return;
    button.addEventListener('click', () => {
      const isVisible = passwordInput.type === 'text';
      passwordInput.type = isVisible ? 'password' : 'text';
      button.textContent = isVisible ? 'Show' : 'Hide';
      button.setAttribute('aria-label', `${isVisible ? 'Show' : 'Hide'} password`);
      button.setAttribute('aria-pressed', String(!isVisible));
    });
  });

  const yearNode = document.getElementById('year');
  if (yearNode) {
    yearNode.textContent = new Date().getFullYear();
  }

  const form = document.getElementById('auth-form');
  const message = document.getElementById('form-message');
  const authTitle = document.getElementById('auth-title');
  const authSubmit = document.getElementById('auth-submit');
  const authSwitch = document.getElementById('auth-switch');
  const forgotPasswordButton = document.getElementById('forgot-password-button');
  const forgotPasswordModal = document.getElementById('forgot-password-modal');
  const forgotPasswordForm = document.getElementById('forgot-password-form');
  const forgotPasswordMessage = document.getElementById('forgot-password-message');
  const nameField = document.getElementById('name');
  const phoneField = document.getElementById('phone');
  let authMode = 'login';
  const apiRequest = async (path, options = {}) => {
    const response = await fetch(`${apiBase}${path}`, {
      headers: { 'Content-Type': 'application/json', ...(options.headers || {}) },
      ...options,
    });
    const result = await response.json().catch(() => ({}));
    if (!response.ok) throw new Error(result.message || 'The request could not be completed.');
    return result;
  };

  document.querySelectorAll('.nav-cta').forEach((authLink) => {
    if (currentUser) {
      authLink.href = 'profile.html';
      authLink.classList.remove('nav-cta');
      authLink.classList.add('profile-link');
      authLink.innerHTML = '<span class="profile-icon" aria-hidden="true">&#128100;</span><span>Profile</span>';
    }
  });

  const profileName = document.getElementById('profile-name');
  const profileEmail = document.getElementById('profile-email');
  const profileForm = document.getElementById('profile-form');
  const profileMessage = document.getElementById('profile-message');
  if (profileName && profileEmail && currentUser) {
    profileName.textContent = currentUser.name;
    profileEmail.textContent = currentUser.email;
  }

  if (profileForm && currentUser) {
    apiRequest(`/profile/${currentUser.id}`).then(({ user }) => {
      localStorage.setItem(loggedInUserKey, JSON.stringify(user));
      profileName.textContent = user.name;
      profileEmail.textContent = user.email;
      ['phone', 'age', 'sport', 'location', 'bio'].forEach((field) => {
        document.getElementById(`profile-${field}`).value = user[field] || '';
      });
    }).catch((error) => { profileMessage.textContent = error.message; });

    profileForm.addEventListener('submit', async (event) => {
      event.preventDefault();
      const phone = document.getElementById('profile-phone').value.trim();
      if (phone && !isValidPhone(phone)) {
        profileMessage.textContent = 'Phone number must contain exactly 10 digits.';
        document.getElementById('profile-phone').focus();
        return;
      }

      const profile = {};
      ['phone', 'age', 'sport', 'location', 'bio'].forEach((field) => {
        profile[field] = document.getElementById(`profile-${field}`).value.trim();
      });
      try {
        const result = await apiRequest(`/profile/${currentUser.id}`, {
          method: 'PUT',
          body: JSON.stringify(profile),
        });
        localStorage.setItem(loggedInUserKey, JSON.stringify(result.user));
        window.alert('User details saved successfully!');
        window.location.replace('index.html');
      } catch (error) {
        profileMessage.textContent = error.message;
      }
    });
  }

  const logoutButton = document.getElementById('logout-button');
  if (logoutButton) {
    logoutButton.addEventListener('click', () => {
      localStorage.removeItem(loggedInUserKey);
      window.location.replace('login.html');
    });
  }

  if (authSwitch) {
    const registering = authMode === 'register';
    authTitle.textContent = registering ? 'Create your SportPath account' : 'Welcome back to SportPath';
    authSubmit.textContent = registering ? 'Register' : 'Login';
    authSwitch.textContent = registering ? 'Already have an account? Login' : 'New to SportPath? Register';
    nameField.required = registering;
    document.querySelector('label[for="name"]')?.classList.toggle('is-hidden', !registering);
    nameField.classList.toggle('is-hidden', !registering);
    forgotPasswordButton?.toggleAttribute('hidden', registering);

    authSwitch.addEventListener('click', () => {
      authMode = authMode === 'register' ? 'login' : 'register';
      const registering = authMode === 'register';
      authTitle.textContent = registering ? 'Create your SportPath account' : 'Welcome back to SportPath';
      authSubmit.textContent = registering ? 'Register' : 'Login';
      authSwitch.textContent = registering ? 'Already have an account? Login' : 'New to SportPath? Register';
      nameField.required = registering;
      document.querySelector('label[for="name"]')?.classList.toggle('is-hidden', !registering);
      nameField.classList.toggle('is-hidden', !registering);
      forgotPasswordButton?.toggleAttribute('hidden', registering);
      message.textContent = '';
    });
  }

  if (form && message) {
    form.addEventListener('submit', async (event) => {
      event.preventDefault();
      const name = nameField?.value.trim();
      const email = document.getElementById('email')?.value.trim().toLowerCase();
      const phone = phoneField?.value.trim();
      const password = document.getElementById('password')?.value;
      if (!email || !phone || !password || (authMode === 'register' && !name)) {
        document.getElementById('details-modal')?.removeAttribute('hidden');
        return;
      }
      if (!isValidPhone(phone)) {
        message.textContent = 'Phone number must contain exactly 10 digits.';
        phoneField?.focus();
        return;
      }
      try {
        if (authMode === 'register') {
          await apiRequest('/register', { method: 'POST', body: JSON.stringify({ name, email, phone, password }) });
          message.textContent = 'Registration complete. Taking you to your profile...';
        }
        const result = await apiRequest('/login', { method: 'POST', body: JSON.stringify({ email, phone, password }) });
        localStorage.setItem(loggedInUserKey, JSON.stringify(result.user));
        const returnTo = new URLSearchParams(window.location.search).get('returnTo');
        window.setTimeout(() => window.location.replace(authMode === 'register' ? 'profile.html' : (returnTo && returnTo !== 'login.html' ? returnTo : 'index.html')), 350);
      } catch (error) {
        message.textContent = error.message;
      }
    });
  }

  forgotPasswordButton?.addEventListener('click', () => {
    forgotPasswordMessage.textContent = '';
    forgotPasswordModal.removeAttribute('hidden');
    document.getElementById('reset-email')?.focus();
  });

  document.getElementById('forgot-password-close')?.addEventListener('click', () => {
    forgotPasswordModal.setAttribute('hidden', '');
    forgotPasswordForm.reset();
  });

  forgotPasswordForm?.addEventListener('submit', async (event) => {
    event.preventDefault();
    const email = document.getElementById('reset-email').value.trim().toLowerCase();
    const phone = document.getElementById('reset-phone').value.trim();
    const newPassword = document.getElementById('reset-password').value;
    const confirmation = document.getElementById('reset-password-confirmation').value;
    if (!isValidPhone(phone)) {
      forgotPasswordMessage.textContent = 'Phone number must contain exactly 10 digits.';
      return;
    }
    if (newPassword.length < 6) {
      forgotPasswordMessage.textContent = 'Password must contain at least 6 characters.';
      return;
    }
    if (newPassword !== confirmation) {
      forgotPasswordMessage.textContent = 'The new passwords do not match.';
      return;
    }
    try {
      const result = await apiRequest('/forgot-password', {
        method: 'POST',
        body: JSON.stringify({ email, phone, new_password: newPassword }),
      });
      forgotPasswordMessage.textContent = result.message;
      forgotPasswordForm.reset();
    } catch (error) {
      forgotPasswordMessage.textContent = error.message;
    }
  });

  const detailsModal = document.getElementById('details-modal');
  document.getElementById('details-modal-close')?.addEventListener('click', () => {
    detailsModal?.setAttribute('hidden', '');
    nameField?.focus();
  });
});
