#include <stdio.h>
#define N 5000000
int main(void){long long s=0; for(int i=0;i<N;i++){int x=(i*37)%101;if(x<25)s+=x*3;else if(x<70)s-=x/2;else s+=x;} printf("%lld\n",s);return 0;}
