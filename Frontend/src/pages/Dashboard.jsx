import React, { useEffect, useState } from "react";
import { getCurrentUser } from "../api/auth";
import { useNavigate } from "react-router-dom";

export default function Dashboard() {
  const [user, setUser] = useState(null);
  const navigate = useNavigate();

  async function loadUser() {
    try {
      const token = localStorage.getItem("access_token");
      const res = await getCurrentUser(token);
      setUser(res.data);
    } catch {
      navigate("/login");
    }
  }

  useEffect(() => {
    loadUser();
  }, []);

  function logout() {
    localStorage.removeItem("access_token");
    navigate("/login");
  }

  if (!user) return <h3>Loading…</h3>;

  return (
    <div>
      <h2>Dashboard</h2>
      <p>Welcome, {user.email}</p>
      <button onClick={logout}>Logout</button>
    </div>
  );
}
