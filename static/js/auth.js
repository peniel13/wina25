const API_BASE_URL = "http://192.168.22.54:8000"; // ✅ à adapter si ton IP ou domaine change

export const AuthService = {
  // 🔐 Connexion avec JWT (email + password)
  login: async (email, password) => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/token/`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ email, password }),
      });

      const data = await response.json();

      if (!response.ok) {
        return {
          success: false,
          error: data.detail || "Email ou mot de passe incorrect.",
        };
      }

      localStorage.setItem("access", data.access);
      localStorage.setItem("refresh", data.refresh);
      localStorage.setItem("user", JSON.stringify(data.user));

      return { success: true, user: data.user };
    } catch (error) {
      return { success: false, error: "Erreur de connexion au serveur." };
    }
  },
  // 🧾 Inscription
  register: async (registrationData) => {
    try {
      const response = await fetch(`${API_BASE_URL}/signup/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(registrationData),
      });

      const data = await response.json();

      if (!response.ok) {
        return { success: false, error: data };
      }

      return { success: true, data };
    } catch (error) {
      return { success: false, error: "Erreur serveur" };
    }
  },

  // 👤 Récupérer le profil
  fetchUserProfile: async () => {
    const access = localStorage.getItem("access");

    const response = await fetch(`${API_BASE_URL}/profile/`, {
      method: "GET",
      headers: {
        Authorization: `Bearer ${access}`,
        "Content-Type": "application/json",
      },
    });

    if (!response.ok) {
      throw new Error("Erreur lors de la récupération du profil utilisateur");
    }

    return await response.json();
  },

  // ✏️ Mise à jour du profil
  updateProfile: async (updatedData) => {
    const access = localStorage.getItem("access");

    const response = await fetch(`${API_BASE_URL}/profile/update/`, {
      method: "PUT",
      headers: {
        Authorization: `Bearer ${access}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify(updatedData),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(JSON.stringify(error));
    }

    const result = await response.json();
    localStorage.setItem("user", JSON.stringify(result.user));
    return result.user;
  },

  // 🔐 Changement de mot de passe
  changePassword: async (oldPassword, newPassword) => {
    const access = localStorage.getItem("access");

    const response = await fetch(`${API_BASE_URL}/change-password/`, {
      method: "PUT",
      headers: {
        Authorization: `Bearer ${access}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ old_password: oldPassword, new_password: newPassword }),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error || "Échec du changement de mot de passe");
    }

    return await response.json();
  },

  // 🔓 Déconnexion
  logout: async () => {
    const refresh = localStorage.getItem("refresh");
    if (!refresh) return;

    await fetch(`${API_BASE_URL}/logout/`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ refresh }),
    });

    localStorage.removeItem("access");
    localStorage.removeItem("refresh");
    localStorage.removeItem("user");
  },

  // 🔍 Accès à l'utilisateur courant
  getCurrentUser: () => {
    const user = localStorage.getItem("user");
    return user ? JSON.parse(user) : null;
  },

  // 🔐 Accès au token
  getAccessToken: () => {
    return localStorage.getItem("access");
  },

  // ♻️ Rafraîchir le token d’accès
  refreshToken: async () => {
    const refresh = localStorage.getItem("refresh");

    const response = await fetch(`${API_BASE_URL}/api/token/refresh/`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ refresh }),
    });

    if (!response.ok) {
      localStorage.clear();
      throw new Error("Échec du rafraîchissement du token");
    }

    const data = await response.json();
    localStorage.setItem("access", data.access);
    return data.access;
  },
};
