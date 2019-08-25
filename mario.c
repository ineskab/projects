#include <cs50.h>
#include <stdio.h>

int get_positive_int(string prompt);  

int main(void)

{

  int n = get_positive_int ("Write the number between 1 and 8: ");
    {for (int i = 1; i <= n; i++)       
        {printf("%*s",n-i,"");
         for (int j = 0; j < i; j++)
            {
               printf("%s","#");
            }
        printf("\n");
      }
  }
}
int get_positive_int(string prompt)
{
    int t;
    do
    {
        t = get_int("%s", prompt);
    }
    while (t >= 8 || t <=1 );
    return t;
}
