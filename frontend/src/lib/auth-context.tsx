"use client";

import React, { createContext, useContext, useState, useEffect } from "react";
import { authAPI } from "./api";

export interface User {
  id: number;
  email: string;
  full_name?: string;
  role: "admin" | "security_manager" | "security_analyst" | "soc_engineer" | string;
  is_active: boolean;
}

interface AuthContextType {
  user: User | null;
  token: string | null;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<boolean>;
  quickLogin: (role: "admin" | "analyst" | "manager" | "soc") => Promise<boolean>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);

  useEffect(() => {
    const savedToken = localStorage.getItem("itbis_token");
    const savedUser = localStorage.getItem("itbis_user");
    if (savedToken && savedUser) {
      setToken(savedToken);
      try {
        setUser(JSON.parse(savedUser));
      } catch (e) {
        localStorage.removeItem("itbis_user");
      }
    }
    setIsLoading(false);
  }, []);

  const login = async (email: string, password: string): Promise<boolean> => {
    try {
      const resp = await authAPI.login({ email, password });
      const { access_token, user: loggedUser } = resp.data;
      setToken(access_token);
      setUser(loggedUser);
      localStorage.setItem("itbis_token", access_token);
      localStorage.setItem("itbis_user", JSON.stringify(loggedUser));
      return true;
    } catch (err) {
      console.error("Login failed:", err);
      return false;
    }
  };

  const quickLogin = async (role: "admin" | "analyst" | "manager" | "soc"): Promise<boolean> => {
    const roleEmailMap = {
      admin: "admin@itbis.security",
      analyst: "analyst@itbis.security",
      manager: "manager@itbis.security",
      soc: "soc@itbis.security",
    };
    const email = roleEmailMap[role];
    return await login(email, "Security@123");
  };

  const logout = () => {
    setUser(null);
    setToken(null);
    localStorage.removeItem("itbis_token");
    localStorage.removeItem("itbis_user");
  };

  return (
    <AuthContext.Provider value={{ user, token, isLoading, login, quickLogin, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
};
