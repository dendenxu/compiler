
/**
 * checkpoint 13
 * feature:
 *      dijkstar shortest path algorithm
 * expected output: 17
 */

int main(void){
	int e[10][10],dis[10],book[10],i,j,m,n,t1,t2,t3,u,v,min;
    n = 6;
    m = 9;
	int inf=99999;
	for(i=1;i<=n;i++)
		for(j=1;j<=n;j++)
			e[i][j]=inf;
    e[1][2] = 1;
    e[1][3] = 12;
    e[2][3] = 9;
    e[2][4] = 3;
    e[3][5] = 5;
    e[4][3] = 4;
    e[4][5] = 13;
    e[4][6] = 15;
    e[5][6] = 4;
	for(i=1;i<=n;i++)
		dis[i]=e[1][i];//初始化dis数组，表示1号顶点到其他顶点的距离 
	for(i=1;i<=n;i++)
		book[i]=0;
	book[i]=1;//记录当前已知第一个顶点的最短路径
	for(i=1;i<=n-1;i++)
		for(i=1;i<=n-1;i++){//找到离一号顶点最近的点 
			min=inf;
			for(j=1;j<=n;j++){
				if(book[j]==0&&dis[j]<min){
					min=dis[j];
					u=j;
				}
			}
			book[u]=1;//记录当前已知离第一个顶点最近的顶点 
			for(v=1;v<=n;v++){
				if(e[u][v]<inf){
					if(dis[v]>dis[u]+e[u][v])
						dis[v]=dis[u]+e[u][v];
				}
			} 
		}
    //0 1 8 4 13 17
	return dis[6];
}