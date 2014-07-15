#include <ctime>
#include <fstream>

//# defines
//# test-proc

int main(int argc, char** argv) {
    //# declerations
    
    std::ifstream datafile_initialize = std::ifstream(argv[1]);
    //# read-in
    //# read-out
    datafile_intialize.close();
    
    std::clock_t start_time = std::clock();
    //# run
    std::clock_t end_time = std::clock();
    
    std::ofstream datafile_out = std::ofstream(argv[2]);
    //# write-out
    datafile_out.close();
    
    std::printf("(%d,)", (int)(end_time-start_time));
    return 0;
}
