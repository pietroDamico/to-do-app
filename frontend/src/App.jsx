import { BrowserRouter, Routes, Route } from 'react-router-dom'

function App() {
  return (
    <BrowserRouter>
      <div className="App">
        <h1>To-Do App</h1>
        <p>Frontend skeleton - to be implemented by LL agents</p>
        <Routes>
          <Route path="/" element={<div>Home</div>} />
        </Routes>
      </div>
    </BrowserRouter>
  )
}

export default App