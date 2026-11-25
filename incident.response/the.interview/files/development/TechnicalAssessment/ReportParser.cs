
using System;
using System.Collections.Generic;

namespace TechnicalAssessment
{
    internal class Program
    {
        static Dictionary<string, string> users = new Dictionary<string, string>()
        {
            { "admin", "@DM1NP4SSW0RD" },
            { "randallpike", "D3v3lop3r" },
            { "guest", "guest" }
        };

        static void Main(string[] args)
        {
            Console.Title = "Technical Assessment - Employee Portal";

            Console.WriteLine("==================================");
            Console.WriteLine("    EMPLOYEE MANAGEMENT PORTAL    ");
            Console.WriteLine("==================================");
            Console.WriteLine();

            Console.Write("Username: ");
            string username = Console.ReadLine() ?? "";

            Console.Write("Password: ");
            string password = Console.ReadLine() ?? "";

            string query = "SELECT * FROM users WHERE username = '"
                         + username + "' AND password = '"
                         + password + "'";

            Console.WriteLine("\n[DEBUG] Executing query:");
            Console.WriteLine(query);

            bool authenticated = false;

            if (username.Contains("' OR '1'='1"))
            {
                authenticated = true;
            }
            else if (users.ContainsKey(username) &&
                     users[username] == password)
            {
                authenticated = true;
            }

            if (authenticated)
            {
                Console.WriteLine("\n[+] Authentication successful!");
                Console.WriteLine("[+] Welcome to the employee portal.");
                Console.WriteLine("[+] FLAG: THM{YOU_THOUGHT_IT_WILL_BE_TH1S_EASY??}");
            }
            else
            {
                Console.WriteLine("\n[-] Invalid credentials.");
            }

            Console.WriteLine("\nPress any key to exit...");
            Console.ReadKey();
        }
    }
}
