#include <stdio.h>
#define N 1400000
static long long a[N];
int main(void){long long s=0;for(int i=0;i<N;i++){s+=(i%19)-9;a[i]=s;}printf("%lld\n",a[N-1]);return 0;}
