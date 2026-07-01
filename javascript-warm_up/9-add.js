#!/usr/bin/node

function add(a, b) {
  return a + b;
}

const x = Number(process.argv[2]);
const y = Number(process.argv[3]);

console.log(add(x, y));
