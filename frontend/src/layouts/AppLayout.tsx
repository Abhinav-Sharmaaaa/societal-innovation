import { Outlet } from "react-router-dom";
import Navbar from "../components/Navbar/Navbar";
import "./AppLayout.css";


/**
 * AppLayout wraps every authenticated route.
 * It renders the shared Navbar at the top and the page content below.
 */
export default function AppLayout() {
  return (
    <div className="app-layout">
      <Navbar />
      <main className="app-main">
        <Outlet />
      </main>
    </div>
  );
}
