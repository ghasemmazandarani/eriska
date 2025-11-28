import { create } from 'zustand';
import api from '@/lib/api';

interface User {
    id: number;
    username: string;
    email: string;
    first_name: string;
    last_name: string;
}

interface AuthState {
    user: User | null;
    isAuthenticated: boolean;
    isLoading: boolean;
    login: (data: any) => Promise<void>;
    register: (data: any) => Promise<void>;
    logout: () => void;
    fetchProfile: () => Promise<void>;
}

export const useAuthStore = create<AuthState>((set) => ({
    user: null,
    isAuthenticated: false,
    isLoading: false,

    login: async (data) => {
        set({ isLoading: true });
        try {
            const response = await api.post('/auth/login/', data);
            localStorage.setItem('access_token', response.data.access);
            localStorage.setItem('refresh_token', response.data.refresh);
            set({ isAuthenticated: true });
            await useAuthStore.getState().fetchProfile();
        } catch (error) {
            throw error;
        } finally {
            set({ isLoading: false });
        }
    },

    register: async (data) => {
        set({ isLoading: true });
        try {
            await api.post('/auth/register/', data);
            // Automatically login after register
            await useAuthStore.getState().login({
                username: data.username,
                password: data.password
            });
        } catch (error) {
            throw error;
        } finally {
            set({ isLoading: false });
        }
    },

    logout: () => {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        set({ user: null, isAuthenticated: false });
        window.location.href = '/login';
    },

    fetchProfile: async () => {
        try {
            const response = await api.get('/auth/profile/');
            set({ user: response.data, isAuthenticated: true });
        } catch (error) {
            set({ user: null, isAuthenticated: false });
        }
    },
}));
