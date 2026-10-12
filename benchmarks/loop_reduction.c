#include <stdio.h>
#define N 4000000
int main(void){long long s=0;for(int i=1;i<N;i++){int v=(i%97);s+=(long long)v*v;}printf("%lld\n",s);return 0;}
