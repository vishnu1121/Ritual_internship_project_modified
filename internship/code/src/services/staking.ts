import { parseEther, formatEther, type Address } from 'viem';

export interface StakingRequest {
  contractAddress: Address;
  amount: bigint;
}

export interface ScheduleStakeRequest extends StakingRequest {
  startDate: string;
  endDate: string;
}

export class StakingService {
  async stake(request: StakingRequest): Promise<boolean> {
    console.log('Staking', formatEther(request.amount), 'ETH to', request.contractAddress);
    return true;
  }

  async scheduleStake(request: ScheduleStakeRequest): Promise<boolean> {
    console.log(
      'Scheduling stake of',
      formatEther(request.amount),
      'ETH from',
      request.startDate,
      'to',
      request.endDate
    );
    return true;
  }

  async getStakedAmount(address: Address): Promise<bigint> {
    return parseEther('1.5'); // Mock value
  }

  async getRewards(address: Address): Promise<bigint> {
    return parseEther('0.25'); // Mock value
  }
}
