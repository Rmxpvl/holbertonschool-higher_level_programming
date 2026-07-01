#!/usr/bin/node

const x = process.argv.slice(2).map(Number);
const length = process.argv.length;
let max = 0;
let secondmax = 0;

if (length === 1) {
  console.log(1);
}

for (const index of x) {
  if (index > max) {
    secondmax = max;
    max = index;
  } else if (index > secondmax) {
    secondmax = index;
  }
}
console.log(secondmax);
