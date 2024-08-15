# Use the official .NET SDK 8.0 image as a build environment
FROM mcr.microsoft.com/dotnet/sdk:8.0 AS build-env

# Set the working directory inside the container
WORKDIR /app

# Copy everything from the booking-microservices directory into the container
COPY ./booking-microservices/ ./

# Restore dependencies for all projects in the solution
RUN dotnet restore "./booking-microservices-sample.sln"

# Build the entire solution
RUN dotnet build "./booking-microservices-sample.sln" -c Release -o /app/build

# Publish all the services
RUN dotnet publish "./src/ApiGateway/src/ApiGateway.csproj" -c Release -o /app/publish/ApiGateway
RUN dotnet publish "./src/Services/Booking/src/Booking/Booking.csproj" -c Release -o /app/publish/Booking
RUN dotnet publish "./src/Services/Flight/src/Flight/Flight.csproj" -c Release -o /app/publish/Flight
RUN dotnet publish "./src/Services/Identity/src/Identity/Identity.csproj" -c Release -o /app/publish/Identity
RUN dotnet publish "./src/Services/Passenger/src/Passenger/Passenger.csproj" -c Release -o /app/publish/Passenger

# Use the official ASP.NET runtime image as the base image
FROM mcr.microsoft.com/dotnet/aspnet:8.0 AS base

# Set the working directory inside the container
WORKDIR /app

# Copy the published applications from the build environment
COPY --from=build-env /app/publish/ApiGateway ./ApiGateway
COPY --from=build-env /app/publish/Booking ./Booking
COPY --from=build-env /app/publish/Flight ./Flight
COPY --from=build-env /app/publish/Identity ./Identity
COPY --from=build-env /app/publish/Passenger ./Passenger

# Expose ports for each service
EXPOSE 80  
EXPOSE 81  
EXPOSE 82  
EXPOSE 83  
EXPOSE 84  

# Run the ApiGateway service by default
ENTRYPOINT ["dotnet", "ApiGateway/ApiGateway.dll"]

# Optionally, you can run the other services as well, or set up multiple containers for each service.
