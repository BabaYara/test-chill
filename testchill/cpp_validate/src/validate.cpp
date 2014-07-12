#include <ctime>
#include <cstdio>

//# test proc

int main(int argc, char** argv) {
    
    //# read in
    //# read out
    
    std::clock_t start_time = std::clock();
    float five_seconds = CLOCKS_PER_SECOND * 5.0;
    int run_count = 0;
    while ((std::clock() - start_time) < five_seconds) {
        //# run
        run_count++;
    }
    std::clock_t end_time = std::clock();
    
    //# write out
    
    printf("(%f,%d)", ((float)(end_time-start_time))/CLOCKS_PER_SECOND, run_count);
    return 0;
}
