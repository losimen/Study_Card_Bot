//
//  HandlerRequest.cpp
//  listener
//
//  Created by Павло Коваль on 27.11.2021.
//

#include "HandlerRequest.hpp"


void HandlerRequest::_requestLogIn(const http_request& request)
{
    
}

void HandlerRequest::_requestSignUp(const http_request& request)
{
    
}


void HandlerRequest::_handle_post(const http_request& request)
{
    std::string urlMain = request.relative_uri().to_string();
    std::string urlRequest = urlMain.substr( urlMain.rfind("/") );
    std::cout << "User main url: "<< urlMain << std::endl;
    std::cout << "User request url: "<< urlRequest << std::endl;

    if (urlRequest == "/sign_up")
    {
        _requestSignUp(request);
    }
    else if(urlRequest == "/login")
    {
        _requestLogIn(request);
    }
    else
    {
        request.reply(status_codes::BadRequest, "There is no request such link");
    }
        
}

void HandlerRequest::AddQueueThread()
{
    const std::string link = "http://localhost:3000/api";

    std::cout << "Your server address: " << link << std::endl;

    http_listener listener(link);

    listener.support(methods::POST, std::bind(&HandlerRequest::_handle_post, this, std::placeholders::_1));
    try
    {
        listener
                .open()
                .then([](){std::cout<<"Starting..."<<std::endl;})
                .wait();
            while (true);
    }
    catch (std::exception const & e)
    {
         std::cout << e.what() << std::endl;
    }
    
}
