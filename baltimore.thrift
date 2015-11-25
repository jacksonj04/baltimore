// Here's a namespace, so we don't break things.
namespace py baltimore

// Here's the service!
service Baltimore {

    // A heartbeat function so we can tell if things are alive or not.
   void heartbeat(),

   // Functions to explicitly control the amplifier
   void amplifierOn(),
   void amplifierOff(),

   // One to get the state of the amplifier
   bool amplifierState(),

   // Play a sound!
   void play(1:string fileName),

   // Stop playing a sound!
   void stop(),

   // Turn hourly bongs on and off.
   void hourChimeOn(),
   void hourChimeOff(),

   // Get the state of the hourly bongs.
   bool hourChimeState(),

}
