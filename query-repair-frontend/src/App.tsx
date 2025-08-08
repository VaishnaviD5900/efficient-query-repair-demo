import { Routes, Route, Navigate, useLocation } from "react-router-dom";
import Home from "./pages/Home";
import QueryEditor from "./pages/QueryEditor";
import Results from "./pages/Results";
import Header from "./components/Header";
import Footer from "./components/Footer";
import Input from "./pages/Input";
import { Toolbar } from "@mui/material";

export default function App() {
  const location = useLocation();
  const isHomePage = location.pathname === "/";

  return (
    <div
      style={{
        display: "flex",
        flexDirection: "column",
        minHeight: "100vh", // ensures footer pushes to bottom when needed
      }}
    >
      <Header />
      <Toolbar />
      <div style={{ flex: 1 }}>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/input" element={<Input/>} />
          <Route path="/editor" element={<QueryEditor />} />
          <Route path="/results" element={<Results />} />
          <Route path="*" element={<Navigate to="/" />} />
        </Routes>
      </div>
      {/* <div style={isHomePage ? { position: "absolute", bottom: 0, width: "100%" } : {}}> */}
        <Footer />
      {/* </div> */}
    </div>
  );
}
