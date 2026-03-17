const express = require("express");
const path = require("path");

const app = express();
const PORT = 3000;

// Middleware
app.use(express.json());
app.use(express.static(path.join(__dirname, "public")));

// Proxy route to Flask backend
app.post("/api/chat", async (req, res) => {
    try {
        const response = await fetch("http://localhost:5000/chat", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(req.body)
        });

        const data = await response.json();
        res.json(data);
    } catch (error) {
        console.error(error);
        res.status(500).json({ error: "Backend connection failed" });
    }
});

// Start server
app.listen(PORT, () => {
    console.log(`🚀 Frontend running at http://localhost:${PORT}`);
});