const express = require('express');
const app = express();
const PORT = 8080;
const HOST = '0.0.0.0';

const fibonacci = (num) => {
  if (num <= 1) return 1;
  return fibonacci(num - 1) + fibonacci(num - 2);
}

app.get('/cpu', (req, res) => {
  fibonacci(35);
  res.send('Fibonacci Sequence');
})

app.listen(PORT, HOST, () => {
  console.log(`Server listening at http://${HOST}:${PORT}`);
})