//http://www.csharphelp.com/archives3/archive554.html
//C# Ping
//By Gerhard Schmeusser

// Minor edits by Rodrigo Benenson
//  MinMax.max->Math.Max
//  CDWPing -> Ping
//  IDWPing -> IPing
//  cmpDWPing->Ping
//  short ping() -> bool ping()  // 1 = success, 0 = failure

// Compile using the command line: mcs Ping.cs -t:library -out:ping.dll


using System;
using System.Net;
using System.Diagnostics;
using System.Net.Sockets;
using System.Collections;

namespace Ping
{
 /// 
 //Implements an Ethernet Ping component
 //Ping is part of the ICMP (Internet Control Message Protocol) which serves
 //Hosts and Routers for the purpose of error messaging and exchanging status and commands.
 //It is part of the IP protocol and therefore cannot be considered as reliable.
 //The following ICMP messages are used here to implement a ping functionality:
 //Echo Request
 //Echo Answer
 
 
 //The interface is pretty straightforward:
 //the ping method performs the network ping and returns success or failure
 //in case of failure ask the ErrorMessage property for the reason
 //
 // There are some properties which you can use for setting and getting information. See the interface below
 //
 //
 //
 //
 //You can use this component as a COM object if
 //you create a COM callable wrapper (CCW) by the following command line programs:
 
    //the typelib is created by the project setting "register for COM interop":
    //regasm bin/debug/cmpDWPing.dll
    //if you also want to manually create a typelib use the following line
    //regasm /tlb:cmpDWPing.tlb bin/debug/cmpDWPing.dll
    
    //use the following lines to register the component in the global assembly cache
    //gacutil /u cmpDWPing
    //gacutil /i bin/debug/cmpDWPing.dll
    //
    //Beforehand justification: Because of the C-style design of the ICMP protocol data structures
    //which are meant to be cast this way and that and therefore not very
    //suitable to a strict language like C#, we have to
    //adopt some pretty awkward code here.
 /// 
 
 interface IPing
 {
     bool   ping(string strHostName);  // true = success, false = failure
     int    Timeout {set;}             //default = 500msec
     int    Repeats {set;}             //default = 0
     int    AvgTime {get;}             //measured average response time
     int    AvgTTL  {get;}             //measured average number of routing nodes the ping traveled
     string ErrorMessage {get;}        //a verbose error message in case of failure 
 }
 
    struct ICMPHeader
    {
        public byte    type;
        public byte    code;
        public ushort  chksum;
        public ushort  id;
        public ushort  seq;
        public ulong   timestamp;
     
        public byte[] toByteArray()
        {
            //If you know a better way to serialize this into a byte array, let me know
            byte[] arResult = new byte[22];
            arResult[0] = this.type;
            arResult[1] = this.code;
            arResult[2] = (byte)chksum;
            arResult[3] = (byte)(chksum >> 8);
            arResult[4] = (byte)(chksum >> 16);
            arResult[5] = (byte)(chksum >> 24);
            arResult[6] = (byte)id;
            arResult[7] = (byte)(id >> 8);
            arResult[8] = (byte)(id >> 16);
            arResult[9] = (byte)(id >> 24);
            arResult[10] = (byte)seq;
            arResult[11] = (byte)(seq >> 8);
            arResult[12] = (byte)(seq >> 16);
            arResult[13] = (byte)(seq >> 24);
            arResult[14] = (byte)timestamp;
            arResult[15] = (byte)(timestamp >> 8);
            arResult[16] = (byte)(timestamp >> 16);
            arResult[17] = (byte)(timestamp >> 24);
            arResult[18] = (byte)(timestamp >> 32);
            arResult[19] = (byte)(timestamp >> 40);
            arResult[20] = (byte)(timestamp >> 48);
            arResult[21] = (byte)(timestamp >> 56);
       
            return arResult;
        }
    }

 public class Ping : IPing
 {
        private int      m_Timeout;   //in msec
        private int[]    m_arTime;    //response times statistic
        private bool[]   m_arResults; //results of pings
        private byte[]   m_arTTL;     //routing stations statistic
        private int      m_idxPing;
        private string   m_strErrorMessage;

     //----------------------------------------------------
 
  
  
  public int Timeout         { set{ m_Timeout = Math.Max(value, 1); }}
  public int Repeats         { set
                               { int n = Math.Max(value, 1);
                                 m_arTime    = new int[n];
                                 m_arTTL     = new byte[n];
                                 m_arResults = new bool[n];
                               }
                             }
  public int AvgTime         { get{ return this.calcAvgTime(); }}
  public int AvgTTL          { get{ return this.calcAvgTTL();  }}
  public string ErrorMessage { get{ return m_strErrorMessage; }}

        public Ping()
        {
            m_arTime    = new int[1];  //size of m_arTime is number of tries
            m_arTTL     = new Byte[1];
            m_arResults = new bool[1];
            m_strErrorMessage = "Don't know what happened";
            m_Timeout = 500;  //msec
        }


        public bool ping(string strHostName)
        {
            m_strErrorMessage = "No error occured";

            this.clearStats();            
            
            short result = 0;
            
            //convert strHostName to an IPEndPoint
            try
            {
                IPEndPoint lep;
                
                //check if strHostname is already a dotted address
                //and create an IPEndpoint from it
                //note: port 7 is for echo but is irrelevant because of the socket type we are going to use
                const int echoPort = 7;
                
                if(true == this.isIPAddress(strHostName))
                {
                    IPAddress ipAddr = IPAddress.Parse(strHostName);
                    lep = new IPEndPoint(ipAddr, echoPort);
                }
                else
                {
                    IPHostEntry lipa = Dns.Resolve(strHostName);
                    lep = new IPEndPoint(lipa.AddressList[0], echoPort);
                }

                //number of tries
                for(m_idxPing = 0; m_idxPing < m_arTime.Length; m_idxPing++)
                {
                    if(true == tryPing(lep))
                    {
                        m_arResults[m_idxPing] = true;
                        result = 1;   //one successful ping = overall success
                    }
                    else
                    {
                        m_arResults[m_idxPing] = false;
                    }
                }
            }
            catch(SocketException ex)
            {
                result = 0;
                m_strErrorMessage = ex.Message;
            }
            catch(Exception ex )
            {
                result = 0;
                m_strErrorMessage = ex.Message;
            }

            return (result == 1);
        }
    
  private bool tryPing(IPEndPoint lep)
  {
      //do the ping
      bool bResult = false;
      
            //create an ICMP socket
            Socket sock  = new Socket(AddressFamily.InterNetwork, SocketType.Raw, ProtocolType.Icmp);

            //set up ICMPHeader structure
            ICMPHeader header = new ICMPHeader();
            header.type         = 8; //ICMP_ECHO type
            header.code         = 0;
            header.id           = Convert.ToUInt16(Process.GetCurrentProcess().Id);  //lossy conversion
            header.seq          = 0;
            header.chksum       = 0;
            DateTime startTime  = DateTime.Now;
            header.timestamp    = Convert.ToUInt64(startTime.Ticks);
                
                
                
            //fill header into byte array
            byte[] arHeader = header.toByteArray();
                
            //create the array which is to be sent
            byte[] arBytes = new byte[arHeader.Length + 32];
                
            byte fill = Convert.ToByte('E');  //arbitrary fill data to be sent
                
            for(int i = 0; i < arBytes.Length; i++)
            {
                arBytes[i] = fill;
            }
                
            //copy header to array which is to be sent
            arHeader.CopyTo(arBytes, 0);
                
            header.chksum = this.generateIPChecksum(arBytes);
            //now this is goofy because after we inserted the checksum into
            //the header we have to recreate the byte array
            arHeader = header.toByteArray();
            arHeader.CopyTo(arBytes, 0);
                         
            sock.SendTo(arBytes, lep);
                
            // check socket receive asnychronously and heed timeout
            if(true == this.isSocketReadible(sock))
            {
                        
                // Creates an IpEndPoint to capture the identity of the sending host.
                IPEndPoint sender1 = new IPEndPoint(IPAddress.Any, 0);
                EndPoint tempRemoteEP = (EndPoint)sender1;

                // Creates a byte buffer to receive the message.
                byte[] receiveBuffer = new byte[1024];

                // Receives datagram from a remote host.  This call blocks!
                int nReceived = sock.ReceiveFrom(receiveBuffer, ref tempRemoteEP);

                bResult = this.verifyReceivedMessage(receiveBuffer, nReceived, arHeader.Length);

                m_arTTL[m_idxPing] = receiveBuffer[8];
            }
            else
            {
                m_strErrorMessage = "Echoing socket is not readible in the given timeout";
            }
      
      //number of routing stations is part of the IP Header
      
            //calculate elapsed time         
            DateTime now         = DateTime.Now;
            TimeSpan elapsedTime = new TimeSpan(now.Ticks - startTime.Ticks);
            m_arTime[m_idxPing]  = elapsedTime.Milliseconds;

      
      return bResult;
  }

        private bool isIPAddress(string strAddress)
        {
            //return true if the address is an IP Address e.g. 192.168.8.111
            //false points to a hostname like "INV111"
            bool bResult = true;
      
            foreach (char ch in strAddress)
            {
                if((false == Char.IsDigit(ch)) && (ch != '.'))
                {
                    bResult = false;
                    break;
                }
            }
      
            return bResult;
        }
  
        private ushort generateIPChecksum(byte[] arBytes)
        {
            //generate an IP checksum based on a given data buffer
            ulong chksum = 0;
            
            int nSize = arBytes.Length;
            int i     = 0;
            
            while(nSize > 1)
            {
                chksum += (ulong)((((ushort)arBytes[i+1]) << 8) + (ushort)arBytes[i]); 
                nSize--;
                nSize--;
                i++;
                i++;
            }
            
            if(nSize > 0)
            {
                chksum += arBytes[i];
            }
            
            chksum =  (chksum >> 16) + (chksum & 0xffff);
            chksum += (chksum >> 16);

            ushort result = (ushort)(~chksum);
            return result;
        }

        private bool isSocketReadible(Socket s)
        {
            //poll socket for data until timeout
            bool bResult = false;
            int n = 0;
            
            while(n < m_Timeout)
            {
                if(true == s.Poll(1000, SelectMode.SelectRead))  //100 usec = 1 msec
                {
                    bResult = true;
                    break;
                }
                
                n++;
            }
            
            return bResult;
        }

        private bool verifyReceivedMessage(byte[] arBytes, int nReceived, int minLengthSent)
        {
            //the first 4 bytes are the length of the IP Header in DWORDS
            int nLengthIPHeader = arBytes[0] & 0x0f;
            nLengthIPHeader *= 4; //in bytes
                
            //enough data received
            if(nLengthIPHeader + minLengthSent > nReceived)
            {
                m_strErrorMessage = "Not enough data echoed";
                return false;
            }
                
            //check if it is an ICMP_ECHOREPLY packet
            if(arBytes[nLengthIPHeader] != 0)
            {
                m_strErrorMessage = "Wrong type of telegram echoed";
                return false;
            }
            
            int nId = arBytes[nLengthIPHeader + 6] + arBytes[nLengthIPHeader + 7] * 256;
                
            //check echoed process id is ours
            if(nId != Convert.ToUInt16(Process.GetCurrentProcess().Id))  //lossy conversion
            {
                m_strErrorMessage = "Received echoed data was not sent by this process";
                return false;
            }
                        
            return true;
        }

  private int calcAvgTime()
  {
      int result = 0;
      
      foreach (int i in m_arTime)
      {
          result += i;
      }
      
      result /= m_arTime.Length;
      return result;
  }


        private int calcAvgTTL()
        {
            int result = 0;
      
            foreach (int i in m_arTTL)
            {
                //only count successful pings
                if(m_arResults[i] == true)
                {
                    result += i;
                }
            }
      
            result /= m_arTTL.Length;
            return result;
        }

        private void clearStats()
        {
            //clear statistical data
            for(int i = 0; i < m_arTime.Length; i++)
            {
                m_arTime[i] = 0;
                m_arTTL[i]  = 0;
            }
        }
 }
}
