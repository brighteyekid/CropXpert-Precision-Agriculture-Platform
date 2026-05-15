import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { useState } from 'react'
import BootSplash from './components/BootSplash/index'
import Home from './pages/Home/index'
import Onboarding from './pages/Onboarding/index'
import Dashboard from './pages/Dashboard/index'

export default function App() {
    const [showSplash, setShowSplash] = useState(true)

    return (
        <>
            {showSplash && <BootSplash onDone={() => setShowSplash(false)} />}
            <BrowserRouter>
                <Routes>
                    <Route path="/" element={<Home />} />
                    <Route path="/onboarding" element={<Onboarding />} />
                    <Route path="/dashboard" element={<Dashboard />} />
                </Routes>
            </BrowserRouter>
        </>
    )
}
