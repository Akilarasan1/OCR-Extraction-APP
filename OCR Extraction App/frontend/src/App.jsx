// import { useState } from 'react';
// import axios from 'axios';

// function App() {
//   const [fileType, setFileType] = useState('image');
//   const [engine, setEngine] = useState('pytesseract');
//   const [file, setFile] = useState(null);
//   const [result, setResult] = useState('');

//   const handleSubmit = async (e) => {
//     e.preventDefault();

//     const formData = new FormData();
//     formData.append('file_type', fileType);
//     formData.append('engine', engine);
//     formData.append('file', file);

//     try {
//       const res = await axios.post('http://localhost:8000/upload', formData);
//       setResult(res.data.text);
//     } catch (err) {
//       setResult('Error: ' + err.message);
//     }
//   };

//   return (
//     <div style={{ maxWidth: 500, margin: '40px auto', fontFamily: 'Arial' }}>
//       <h2>OCR Uploader</h2>
//       <form onSubmit={handleSubmit}>
//         <label>
//           File Type:
//           <select value={fileType} onChange={(e) => setFileType(e.target.value)}>
//             <option value="image">Image</option>
//             <option value="pdf">PDF</option>
//           </select>
//         </label>
//         <br /><br />
//         <label>
//           OCR Engine:
//           <select value={engine} onChange={(e) => setEngine(e.target.value)}>
//             <option value="pytesseract">Pytesseract</option>
//             <option value="paddle">Paddle</option>
//             <option value="google">Google</option>
//           </select>
//         </label>
//         <br /><br />
//         <input type="file" onChange={(e) => setFile(e.target.files[0])} required />
//         <br /><br />
//         <button type="submit">Upload</button>
//       </form>
//       <h3>OCR Result</h3>
//       <pre style={{ background: '#f4f4f4', padding: '10px' }}>{result}</pre>
//     </div>
//   );
// }

// export default App;


import { useState } from 'react';
import axios from 'axios';

function App() {
  const [fileType, setFileType] = useState('image');
  const [engine, setEngine] = useState('pytesseract');
  const [file, setFile] = useState(null);
  const [result, setResult] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();

    const formData = new FormData();
    formData.append('file_type', fileType);
    formData.append('engine', engine);
    formData.append('file', file);

    try {
      const response = await axios.post('http://localhost:6999/route_selector', formData);
      setResult(JSON.stringify(response.data, null, 2));
    } catch (error) {
      setResult('Error: ' + error.message);
    }
  };

  return (
    <div style={{ maxWidth: 500, margin: '40px auto', fontFamily: 'Arial' }}>
      <h2>OCR Uploader</h2>
      <form onSubmit={handleSubmit}>
        <label>
          File Type:
          <select value={fileType} onChange={(e) => setFileType(e.target.value)}>
            <option value="image">Image</option>
            <option value="pdf">PDF</option>
          </select>
        </label>
        <br /><br />
        <label>
          OCR Engine:
          <select value={engine} onChange={(e) => setEngine(e.target.value)}>
            <option value="pytesseract">Pytesseract</option>
            <option value="paddle">Paddle</option>
            <option value="google">Google</option>
          </select>
        </label>
        <br /><br />
        <input type="file" onChange={(e) => setFile(e.target.files[0])} required />
        <br /><br />
        <button type="submit">Upload</button>
      </form>
      <h3>OCR Result</h3>
      <pre style={{ background: '#f4f4f4', padding: '10px' }}>{result}</pre>
    </div>
  );
}

export default App;
