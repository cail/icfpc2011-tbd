
#include <boost/python/class.hpp>
#include <boost/python/module.hpp>
#include <boost/python/def.hpp>
#include <iostream>
#include <ostream>
#include <string>

namespace libcpp
{
    class printer
    {
        private:
            std::string str_;

        public:
            printer(const std::string& str): str_(str) { }

            void prn() const
            {
                std::cout << str_ << std::endl;
            }
    };

    std::string dup(const std::string& str)
    {
        return str + str;
    }
}

BOOST_PYTHON_MODULE(libcpp)
{
    using namespace boost::python;
    
    class_<libcpp::printer>("printer", init<std::string>())
            .def("prn", &libcpp::printer::prn)
            ;
    
    def("dup", libcpp::dup);
}

