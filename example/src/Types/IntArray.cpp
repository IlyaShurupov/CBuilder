
#include "IntArray.h"

IntArray::IntArray(int n) {
	buff = new int[n];
}

int& IntArray::operator[](int idx) {
	return buff[idx];
}

IntArray::~IntArray() {
	delete[] buff;
}