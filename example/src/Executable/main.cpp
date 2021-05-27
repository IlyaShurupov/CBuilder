

#include "Types.h"

#include "ModuleA.h"
#include "ModuleB.h"
#include "ModuleC.h"

#include <iostream>


int main() {
	IntArray array(3);
	ModuleA(array);
	ModuleB(array);
	ModuleC(array);

	std::cout << "ModuleA: " << array[0] << " ModuleB: "<< array[1] << " ModuleC: "<< array[2];

	int tmp;
	std::cin >> tmp;
}