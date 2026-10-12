#include <stdio.h>
#define N 7000000
int main(void){long long a=0,b=0;for(int i=0;i<N;i++){int x=(i*17+13)%257;if(x&1)a++;if(x>128)b+=x;}printf("%lld %lld\n",a,b);return 0;}
