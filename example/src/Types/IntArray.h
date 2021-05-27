#pragma once

class IntArray {

	int* buff = nullptr;
	int len = 0;

public:
	IntArray(int n);
	int& operator[](int idx);
	~IntArray();
};