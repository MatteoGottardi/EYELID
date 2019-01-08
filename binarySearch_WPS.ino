#include <FS.h>
#include <ESP8266WiFi.h>

const String dataFile = "/byteTest.bin";
const String indexFile = "/indexSo.bin";
const unsigned long indexSize = 2580;

File file_idx;
File file_data;

void setup()
{
  Serial.begin(115200);
  Serial.println(__FILE__);
  
  SPIFFS.begin();
  WiFi.mode(WIFI_STA);
  WiFi.disconnect();
}

void loop()
{
  int n = WiFi.scanNetworks();
  file_idx = SPIFFS.open(indexFile, "r");
  file_data = SPIFFS.open(dataFile, "r");

  unsigned long dt = millis();
  
  if (n==0)
    Serial.println("No network");
  else 
  {
    Serial.println("found "+ String(n) +" network");
    
    for (int w=0; w<n; w++)
    {
      byte *bssid = WiFi.BSSID(w);
      unsigned long beginIdx;
      unsigned long endIdx;
      
      if (findIndex(indexFile, bssid, beginIdx, endIdx))
      {
        float lat, lng;
        if (getPositionWifi(dataFile, bssid, beginIdx, endIdx, lat, lng))
        {
          char t[32] = "";
          array_to_string(bssid, 6, t);
          Serial.print("Found: ");
          Serial.print(t);
          Serial.println(" lat: "+ String(lat, 5) +", long: "+ String(lng, 5));
        } else {
          char t[32] = "";
          array_to_string(bssid, 6, t);
          Serial.print("Not found: ");
          Serial.println(t);
        }
      } else
        Serial.println("index problem");
    }
  }

  Serial.println("dt: "+ String(millis() - dt));

  file_idx.close();
  file_data.close();
  delay(15000);
}


/*
 *  TODO: use file.seek() and file.read() instead of file.readStringUntil()
 * 
 *  find the first 2 byte of the wifi
 *  return  true if index found
 *          false when EOF is reach and nothing is found
 */
bool findIndex (String fileName, byte target[], unsigned long &beginIdx, unsigned long &endIdx)
{
  int record_size = 10;
  int num_record = indexSize/record_size;

  int p, u, m;
  unsigned long pos;
  byte m_buf[6], u_buf[6], d_buf[6];
  p = 0;
  u = num_record - 1;
  while (p <= u && p >= 0 && u <= num_record)
  {
    m = (p + u) / 2;
    pos = m * record_size;

    file_idx.seek(pos);
    for(int i=0; i<6; i++)
      m_buf[i] = file_idx.read();

    file_idx.seek(pos - record_size);
    for(int i=0; i<6; i++)
      u_buf[i] = file_idx.read();

    file_idx.seek(pos + record_size);
    for(int i=0; i<6; i++)
      d_buf[i] = file_idx.read();

    if (bssidOperator(target, '=', m_buf))
    {
      byte buf[4];
      file_idx.seek(pos+6);
      file_idx.read(buf, 4);    
      beginIdx =* (unsigned long*)(&buf);
      endIdx = 0;
      return true;
    }

    if (bssidOperator(target, '>', u_buf) && bssidOperator(target, '<', m_buf))
    {
      byte buf[4];
      file_idx.seek(pos - 4);
      file_idx.read(buf, 4);    
      beginIdx =*(unsigned long*)(&buf);
      file_idx.seek(pos + 6);
      file_idx.read(buf, 4);
      endIdx =*(unsigned long*)(&buf);
      return true;
    }

    if (bssidOperator(target, '>', m_buf) && bssidOperator(target, '<', d_buf))
    {
      byte buf[4];
      file_idx.seek(pos + 6);
      file_idx.read(buf, 4);    
      beginIdx =*(unsigned long*)(&buf);
      file_idx.seek(pos + 16);
      file_idx.read(buf, 4);
      endIdx =*(unsigned long*)(&buf);
      return true;
    } 
    
    if (bssidOperator(m_buf, '<', target))
      p = m + 1;
    else
      u = m - 1;
  }

  beginIdx = 0;
  endIdx = indexSize;
  return false;
}


bool getPositionWifi (String fileName, byte target[], unsigned long pos_begin, unsigned long pos_end, float &lat, float &lng)
{
  int record_size = 14;

  if (pos_end ==0)
  {
    byte p_buf[6];
    file_data.seek(pos_begin);
    for(int i=0; i<6; i++)
      p_buf[i] = file_data.read();
    if (bssidOperator(target, '=', p_buf))
    {
      byte buf[4];
      file_data.seek(pos_begin + 6);
      file_data.read(buf, 4);    
      lat =* (float*)(&buf);
      file_data.seek(pos_begin + 10);
      file_data.read(buf, 4);
      lng =* (float*)(&buf);
      return true;
    }
    return false; 
  }
  
  int p, u, m;
  unsigned long pos;
  byte m_buf[6];
  p = pos_begin/record_size;
  u = (pos_end/record_size) - 1;
  while (p <= u && p >= pos_begin/record_size && u <= (pos_end/record_size) - 1)
  {
    m = (p + u) / 2;
    pos = m * record_size;
    
    file_data.seek(pos);
    for(int i=0; i<6; i++)
      m_buf[i] = file_data.read();

    if (bssidOperator(target, '=', m_buf))
    {
      byte buf[4];
      file_data.seek(pos+6);
      file_data.read(buf, 4);    
      lat =* (float*)(&buf);
      file_data.seek(pos+10);
      file_data.read(buf, 4);
      lng =* (float*)(&buf);
      return true;
    }

    if (bssidOperator(m_buf, '<', target))
      p = m + 1;
    else
      u = m - 1;
  }

  return false;
}


bool bssidOperator(byte wifi[], char op, byte input[])
{ 
  if (op == '<') {
    for (int i=0; i<6; i++)
    {
      if (wifi[i] != input[i] && wifi[i] < input[i])
      {
        return true;
      } else if (wifi[i] != input[i])
        return false;
    }
  } else if (op == '>') {
    for (int i=0; i<6; i++)
    {
      if (wifi[i] != input[i] && wifi[i] > input[i])
      {
        return true;
      } else if (wifi[i] != input[i])
        return false;
    }
  } else if (op == '=') {
    for (int i=0; i<6; i++)
      if (wifi[i] != input[i])
        return false;
      return true;
  }
    
  return false;
}


void array_to_string(byte array[], unsigned int len, char buffer[])
{
    for (unsigned int i = 0; i < len; i++)
    {
        byte nib1 = (array[i] >> 4) & 0x0F;
        byte nib2 = (array[i] >> 0) & 0x0F;
        buffer[i*2+0] = nib1  < 0xA ? '0' + nib1  : 'A' + nib1  - 0xA;
        buffer[i*2+1] = nib2  < 0xA ? '0' + nib2  : 'A' + nib2  - 0xA;
    }
    buffer[len*2] = '\0';
}



